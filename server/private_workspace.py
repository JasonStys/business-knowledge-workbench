# @index-begin
# @symbol variable/parameter: HISTORY_RECOVERY_BYTES L65
# @symbol function/class: atomic_json L68
# @symbol variable/parameter: path L68
# @symbol variable/parameter: value L68
# @symbol variable/parameter: descriptor L70
# @symbol variable/parameter: name L70
# @symbol variable/parameter: stream L72
# @symbol function/class: InstanceLock L81
# @symbol function/class: __init__ L84
# @symbol variable/parameter: self L84
# @symbol function/class: close L106
# @symbol function/class: Workspaces L111
# @symbol variable/parameter: root L114
# @symbol variable/parameter: allowed L120
# @symbol variable/parameter: p L129
# @symbol function/class: archive L149
# @symbol variable/parameter: owner L149
# @symbol variable/parameter: c L153
# @symbol variable/parameter: session L158
# @symbol function/class: status L158
# @symbol variable/parameter: config L160
# @symbol variable/parameter: encoded L170
# @symbol variable/parameter: salt L170
# @symbol function/class: unlock L170
# @symbol variable/parameter: key L174
# @symbol variable/parameter: current L175
# @symbol variable/parameter: proof L179
# @symbol variable/parameter: nonce L192
# @symbol variable/parameter: provider_path L230
# @symbol variable/parameter: settings L234
# @symbol variable/parameter: k L238
# @symbol variable/parameter: v L238
# @symbol function/class: require L247
# @symbol variable/parameter: force L253
# @symbol function/class: save L253
# @symbol function/class: remove_active L264
# @symbol function/class: lock L276
# @symbol function/class: delete L290
# @index-end
"""Jason Stys: exclusive account-scoped document service, encrypted documents/settings, and recoverable shutdown.

Locked archives do not protect active source/memory from the device's OS owner or administrator.
"""

import asyncio
import base64
import json
import os
import secrets
import shutil
import tempfile
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from starlette.concurrency import run_in_threadpool

from server.accounts import Accounts, decode_field
from server.ai import CompatibleAdapter, ExtractiveAdapter
from server.app import create_app
from server.permissions import protect_directory
from server.vault import AAD, decrypt_workspace, encrypt_workspace, members, signature

# Read recovery reserve exceeds the write stop, so a last in-flight job cannot lock out exports.
HISTORY_RECOVERY_BYTES = 160 * 1024**2


def atomic_json(path: Path, value: dict):
    """Atomically publish only a managed marker/config; retain the prior complete file on failure."""
    descriptor, name = tempfile.mkstemp(prefix=".publish-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(value, stream, allow_nan=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


class InstanceLock:
    """One process owns a dedicated account root; no second launcher may clean its active files."""

    def __init__(self, path: Path):
        """Hold a nonblocking OS advisory file lock until this document service closes."""
        self.stream = path.open("a+b")
        self.stream.seek(0)
        self.stream.write(b"1")
        self.stream.flush()
        self.stream.seek(0)
        try:
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(self.stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(self.stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            self.stream.close()
            raise ValueError(
                "Another application instance uses this account root; close it first"
            ) from None

    def close(self):
        """Release only this process's held descriptor."""
        self.stream.close()


class Workspaces:
    """One unlocked account engine, with separately vault-proven sessions and no admin read API."""

    def __init__(self, root: Path):
        """Protect a dedicated new root; leave old legacy/developer/desktop data untouched."""
        if root.is_symlink() or root.is_junction():
            raise ValueError("A private data root cannot be a link")
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        allowed = {
            "accounts.sqlite",
            "accounts.sqlite-wal",
            "accounts.sqlite-shm",
            "instance.lock",
            "active",
            "active-owner.json",
            "encrypted",
        }
        if any(p.name not in allowed for p in self.root.iterdir()):
            raise ValueError(
                "Choose an empty dedicated account directory; unrelated existing files were preserved"
            )
        protect_directory(self.root)
        self.instance = InstanceLock(self.root / "instance.lock")
        self.accounts = Accounts(self.root / "accounts.sqlite")
        self.active = self.root / "active"
        self.marker = self.root / "active-owner.json"
        self.archives = self.root / "encrypted"
        self.archives.mkdir(exist_ok=True, mode=0o700)
        self.owner = self.key = self.app = self.context = self.saved_signature = None
        self.sessions = set()
        self.token = secrets.token_urlsafe(32)
        self.requests = asyncio.Lock()
        self.failed = False
        if self.marker.exists() != self.active.exists():
            self.instance.close()
            raise ValueError("Incomplete recovery state; preserve this directory and seek support")

    def archive(self, owner: str) -> Path:
        """Use only server-generated opaque account IDs as encrypted archive names."""
        if not owner or any(
            c not in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-"
            for c in owner
        ):
            raise ValueError("Invalid internal owner")
        return self.archives / (owner + ".kbwvault")

    def status(self, owner: str, session: str):
        """Never expose another owner's alias/history; require this session to prove its vault phrase."""
        config = self.accounts.vault(owner)["envelope"]
        return {
            "configured": bool(config),
            "salt": config["salt"] if config else None,
            "unlocked": self.owner == owner and session in self.sessions,
            "engine_busy": self.owner is not None and self.owner != owner,
            "recovery_pending": self.marker.exists() and self.owner is None,
            "save_failed": self.failed,
        }

    async def unlock(self, owner: str, session: str, encoded: str, salt: str | None):
        """Authenticate the independent key, recover only its owner, then enter its genuine document service lifecycle."""
        if self.owner is not None and self.owner != owner:
            raise ValueError("Another account has this local engine unlocked; it must lock first")
        key = decode_field(encoded, 32, 32)
        current = self.accounts.vault(owner)
        config = current["envelope"]
        if config:
            try:
                proof = AESGCM(key).decrypt(
                    decode_field(config["iv"], 12, 12), decode_field(config["proof"], 16, 256), AAD
                )
                if proof != b"business-knowledge-local-key-v1":
                    raise ValueError()
            except Exception:
                raise ValueError(
                    "Cannot unlock: wrong vault phrase or damaged key settings"
                ) from None
        else:
            if self.marker.exists():
                raise ValueError("The interrupted account's owner must recover it first")
            decode_field(salt or "", 16, 16)
            nonce = secrets.token_bytes(12)
            config = {
                "salt": salt,
                "iv": base64.b64encode(nonce).decode(),
                "proof": base64.b64encode(
                    AESGCM(key).encrypt(nonce, b"business-knowledge-local-key-v1", AAD)
                ).decode(),
            }
            if not self.accounts.save(owner, config, current["revision"]):
                raise ValueError("Account changed; refresh")
        if self.owner == owner:
            self.sessions.add(session)
            return
        if self.marker.exists():
            if json.loads(self.marker.read_text())["owner"] != owner:
                raise ValueError("The interrupted account's owner must recover it first")
        else:
            if self.archive(owner).exists():
                try:
                    await run_in_threadpool(
                        decrypt_workspace, self.archive(owner), self.active, key
                    )
                except Exception:
                    raise ValueError(
                        "Cannot unlock damaged archive; existing files were preserved"
                    ) from None
            else:
                self.active.mkdir(mode=0o700)
            atomic_json(self.marker, {"owner": owner})
        members(self.active)
        if (self.active / "workbench.sqlite").exists() and (
            self.active / "workbench.sqlite"
        ).stat().st_size > HISTORY_RECOVERY_BYTES:
            raise ValueError(
                "History exceeds the recovery reserve; preserve this archive and seek support"
            )
        self.app = create_app(self.active / "workbench.sqlite", demo=False, private_mode=True)
        self.app.state.ai_adapter = ExtractiveAdapter()
        provider_path = self.active / "provider.private.json"
        if provider_path.exists():
            if provider_path.stat().st_size > 16000:
                raise ValueError("Provider settings exceed limit")
            settings = json.loads(provider_path.read_text())
            if settings.get("endpoint"):
                from server.private_api import Settings

                Settings.model_validate({k: v for k, v in settings.items() if k != "revision"})
                self.app.state.ai_adapter = CompatibleAdapter(
                    settings["endpoint"], settings["model"], settings.get("key", "")
                )
        self.owner, self.key = owner, key
        self.sessions = {session}
        self.saved_signature = None
        await run_in_threadpool(self.save, True)

    def require(self, owner: str, session: str):
        """A login cookie alone cannot join an already-unlocked account without key proof."""
        if self.owner != owner or session not in self.sessions or self.app is None:
            raise ValueError("Unlock this session's private workspace first")
        return self.app

    def save(self, force=False):
        """O(F) unchanged checks; O(S) streaming encryption only after idle data changes."""
        if self.owner is None:
            return {"saved": False}
        current = signature(self.active)
        if current != self.saved_signature:
            encrypt_workspace(self.active, self.archive(self.owner), self.key)
            self.saved_signature = current
        self.failed = False
        return {"saved": True}

    def remove_active(self, owner: str):
        """Delete only the exact managed working directory after validating its owner and resolved scope."""
        if (
            self.active.resolve() != self.root / "active"
            or self.active.is_symlink()
            or self.active.is_junction()
            or json.loads(self.marker.read_text())["owner"] != owner
        ):
            raise ValueError("Recovery ownership/path check failed")
        shutil.rmtree(self.active)
        self.marker.unlink()

    async def lock(self, owner: str):
        """Cancel/clean only this account's containers before sealing; preserve all recovery data on failure."""
        if self.owner != owner:
            return {"locked": True}
        try:
            await run_in_threadpool(self.save, True)
            await run_in_threadpool(self.remove_active, owner)
        except Exception:
            self.failed = True
            raise
        self.owner = self.key = self.app = self.saved_signature = None
        self.sessions.clear()
        return {"locked": True}

    async def delete(self, owner: str):
        """Current-password-authorized removal affects only this account, not another account's active engine."""
        if self.owner == owner:
            await self.lock(owner)
        elif self.marker.exists() and json.loads(self.marker.read_text())["owner"] == owner:
            await run_in_threadpool(self.remove_active, owner)
        self.archive(owner).unlink(missing_ok=True)

    async def close(self):
        """Attempt secure shutdown; failed snapshots remain recoverable rather than erased."""
        try:
            if self.owner:
                await self.lock(self.owner)
        finally:
            self.instance.close()
