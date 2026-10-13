# @index-begin
# @symbol variable/parameter: SESSION_SECONDS L66
# @symbol variable/parameter: IDLE_SECONDS L67
# @symbol variable/parameter: HASH_SLOTS L68
# @symbol function/class: digest L71
# @symbol variable/parameter: value L71
# @symbol variable/parameter: password L76
# @symbol function/class: password_hash L76
# @symbol variable/parameter: salt L76
# @symbol variable/parameter: key L80
# @symbol function/class: password_matches L86
# @symbol variable/parameter: stored L86
# @symbol variable/parameter: _ L89
# @symbol variable/parameter: version L89
# @symbol function/class: Accounts L97
# @symbol function/class: __init__ L100
# @symbol variable/parameter: path L100
# @symbol variable/parameter: self L100
# @symbol function/class: connection L122
# @symbol variable/parameter: db L124
# @symbol function/class: throttle L133
# @symbol variable/parameter: window L133
# @symbol variable/parameter: now L135
# @symbol variable/parameter: row L139
# @symbol variable/parameter: count L140
# @symbol function/class: register L147
# @symbol variable/parameter: username L147
# @symbol variable/parameter: hashed L150
# @symbol function/class: login L160
# @symbol variable/parameter: valid L164
# @symbol variable/parameter: owner L167
# @symbol function/class: session L167
# @symbol function/class: owner L184
# @symbol variable/parameter: token L184
# @symbol function/class: revoke L196
# @symbol function/class: vault L201
# @symbol variable/parameter: envelope L213
# @symbol variable/parameter: revision L213
# @symbol function/class: save L213
# @symbol variable/parameter: recovery L226
# @symbol function/class: reset L226
# @symbol variable/parameter: fresh L234
# @symbol variable/parameter: updated L236
# @symbol function/class: delete L245
# @symbol function/class: decode_field L259
# @symbol variable/parameter: maximum L259
# @symbol variable/parameter: minimum L259
# @symbol variable/parameter: result L262
# @index-end
"""Jason Stys: isolated account/session store; private local authentication and encrypted-vault configuration.

Passwords are scrypt hashes, session/recovery secrets are SHA-256 digests of random
256-bit values. No project content, encryption phrase, administrator read API or telemetry.
"""

import base64
import hashlib
import json
import secrets
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path
from threading import BoundedSemaphore

SESSION_SECONDS = 8 * 3600
IDLE_SECONDS = 30 * 60
HASH_SLOTS = BoundedSemaphore(2)


def digest(value: str) -> str:
    """Hash a high-entropy opaque secret for lookup, never a human password."""
    return hashlib.sha256(value.encode()).hexdigest()


def password_hash(password: str, salt: str | None = None) -> str:
    """scrypt N=2^17,r=8,p=1 with a random salt; bound passwords before calling."""
    salt = salt or secrets.token_hex(32)
    with HASH_SLOTS:
        key = hashlib.scrypt(
            password.encode(), salt=bytes.fromhex(salt), n=131072, r=8, p=1, maxmem=192 * 1024**2
        )
    return f"scrypt-v1${salt}${key.hex()}"


def password_matches(password: str, stored: str) -> bool:
    """Constant-time comparison of a fixed-version hash; malformed hashes fail closed."""
    try:
        version, salt, _ = stored.split("$")
        return version == "scrypt-v1" and secrets.compare_digest(
            password_hash(password, salt), stored
        )
    except (ValueError, TypeError):
        return False


class Accounts:
    """Short SQLite transactions with session expiry, rate limits and vault CAS writes."""

    def __init__(self, path: Path):
        """Create private runtime-only tables; never open the legacy plaintext database."""
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        # A stable dummy hash avoids password-hash timing differences for missing users.
        self.dummy = password_hash(secrets.token_urlsafe(32))
        with self.connection() as db:
            db.executescript("""
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS accounts (
                    id TEXT PRIMARY KEY, username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL, recovery TEXT NOT NULL, created INTEGER NOT NULL);
                CREATE TABLE IF NOT EXISTS sessions (
                    token TEXT PRIMARY KEY, owner TEXT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
                    expires INTEGER NOT NULL, touched INTEGER NOT NULL);
                CREATE TABLE IF NOT EXISTS vaults (
                    owner TEXT PRIMARY KEY REFERENCES accounts(id) ON DELETE CASCADE,
                    envelope TEXT NOT NULL, revision INTEGER NOT NULL);
                CREATE TABLE IF NOT EXISTS limits (key TEXT PRIMARY KEY, started INTEGER, count INTEGER);
            """)

    @contextmanager
    def connection(self):
        """Close connections on every path; foreign keys enforce cascading deletion."""
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        try:
            with db:
                yield db
        finally:
            db.close()

    def throttle(self, key: str, maximum: int, window: int = 300) -> bool:
        """Persist bounded-window counters across restarts; store no raw IP addresses."""
        now = int(time.time())
        with self.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("DELETE FROM limits WHERE started < ?", (now - window,))
            row = db.execute("SELECT count FROM limits WHERE key=?", (digest(key),)).fetchone()
            count = row[0] + 1 if row else 1
            db.execute(
                "INSERT INTO limits VALUES(?,?,?) ON CONFLICT(key) DO UPDATE SET count=?",
                (digest(key), now, count, count),
            )
            return count <= maximum

    def register(self, username: str, password: str):
        """Create a real account and a once-shown random login recovery code."""
        owner, recovery = secrets.token_urlsafe(24), secrets.token_urlsafe(32)
        hashed = password_hash(password)
        with self.connection() as db:
            if db.execute("SELECT count(*) FROM accounts").fetchone()[0] >= 10000:
                raise ValueError("Registration capacity reached")
            db.execute(
                "INSERT INTO accounts VALUES(?,?,?,?,?)",
                (owner, username, hashed, digest(recovery), int(time.time())),
            )
        return owner, recovery

    def login(self, username: str, password: str):
        """Authenticate without exposing whether an account exists."""
        with self.connection() as db:
            row = db.execute("SELECT * FROM accounts WHERE username=?", (username,)).fetchone()
        valid = password_matches(password, row["password"] if row else self.dummy)
        return row["id"] if row and valid else None

    def session(self, owner: str) -> str:
        """Rotate the random bearer cookie; bound stored sessions to ten per user."""
        token, now = secrets.token_urlsafe(32), int(time.time())
        with self.connection() as db:
            db.execute(
                "DELETE FROM sessions WHERE expires<=? OR touched<=?", (now, now - IDLE_SECONDS)
            )
            db.execute(
                "INSERT INTO sessions VALUES(?,?,?,?)",
                (digest(token), owner, now + SESSION_SECONDS, now),
            )
            db.execute(
                "DELETE FROM sessions WHERE token IN (SELECT token FROM sessions WHERE owner=? ORDER BY touched DESC LIMIT -1 OFFSET 10)",
                (owner,),
            )
        return token

    def owner(self, token: str):
        """Enforce absolute/idle expiry before identifying a session's account."""
        now = int(time.time())
        with self.connection() as db:
            row = db.execute(
                "SELECT accounts.id, username FROM sessions JOIN accounts ON owner=accounts.id WHERE token=? AND expires>? AND touched>?",
                (digest(token), now, now - IDLE_SECONDS),
            ).fetchone()
            if row:
                db.execute("UPDATE sessions SET touched=? WHERE token=?", (now, digest(token)))
            return dict(row) if row else None

    def revoke(self, token: str):
        """Log out exactly the presented session."""
        with self.connection() as db:
            db.execute("DELETE FROM sessions WHERE token=?", (digest(token),))

    def vault(self, owner: str):
        """Return only this session owner's ciphertext and revision, never another owner ID."""
        with self.connection() as db:
            row = db.execute(
                "SELECT envelope, revision FROM vaults WHERE owner=?", (owner,)
            ).fetchone()
            return (
                {"envelope": json.loads(row[0]), "revision": row[1]}
                if row
                else {"envelope": None, "revision": 0}
            )

    def save(self, owner: str, envelope: dict, revision: int):
        """Compare-and-swap the whole encrypted vault atomically; conflicts never overwrite."""
        with self.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT revision FROM vaults WHERE owner=?", (owner,)).fetchone()
            if (row[0] if row else 0) != revision:
                return False
            db.execute(
                "INSERT INTO vaults VALUES(?,?,?) ON CONFLICT(owner) DO UPDATE SET envelope=excluded.envelope,revision=excluded.revision",
                (owner, json.dumps(envelope, separators=(",", ":")), revision + 1),
            )
        return True

    def reset(self, username: str, recovery: str, password: str):
        """Recovery rotates login credentials/recovery code, not vault encryption keys."""
        with self.connection() as db:
            row = db.execute(
                "SELECT id,recovery FROM accounts WHERE username=?", (username,)
            ).fetchone()
        if not row or not secrets.compare_digest(row["recovery"], digest(recovery)):
            return None
        fresh, hashed = secrets.token_urlsafe(32), password_hash(password)
        with self.connection() as db:
            updated = db.execute(
                "UPDATE accounts SET password=?,recovery=? WHERE id=? AND recovery=?",
                (hashed, digest(fresh), row["id"], row["recovery"]),
            )
            if not updated.rowcount:
                return None
            db.execute("DELETE FROM sessions WHERE owner=?", (row["id"],))
        return fresh

    def delete(self, owner: str, password: str):
        """Require the current password, then cascade live account/session/vault deletion."""
        with self.connection() as db:
            row = db.execute("SELECT password FROM accounts WHERE id=?", (owner,)).fetchone()
        if not row or not password_matches(password, row[0]):
            return False
        with self.connection() as db:
            return bool(
                db.execute(
                    "DELETE FROM accounts WHERE id=? AND password=?", (owner, row[0])
                ).rowcount
            )


def decode_field(value: str, minimum: int, maximum: int) -> bytes:
    """Reject malformed or oversized base64 before encrypted envelope storage."""
    try:
        result = base64.b64decode(value, validate=True)
    except ValueError as error:
        raise ValueError("Invalid encrypted envelope") from error
    if not minimum <= len(result) <= maximum:
        raise ValueError("Invalid encrypted envelope")
    return result
