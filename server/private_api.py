# @index-begin
# @symbol variable/parameter: CSP L130
# @symbol variable/parameter: HISTORY_STOP_BYTES L131
# @symbol function/class: Boundary L134
# @symbol function/class: __init__ L137
# @symbol variable/parameter: self L137
# @symbol function/class: __call__ L143
# @symbol variable/parameter: receive L143
# @symbol variable/parameter: scope L143
# @symbol variable/parameter: send L143
# @symbol variable/parameter: raw L147
# @symbol variable/parameter: headers L148
# @symbol variable/parameter: k L148
# @symbol variable/parameter: v L148
# @symbol function/class: guarded L150
# @symbol variable/parameter: message L150
# @symbol function/class: deny L189
# @symbol variable/parameter: detail L189
# @symbol variable/parameter: status L189
# @symbol variable/parameter: cookies L220
# @symbol variable/parameter: token L225
# @symbol variable/parameter: account L226
# @symbol variable/parameter: chunks L234
# @symbol variable/parameter: length L234
# @symbol variable/parameter: delivered L246
# @symbol function/class: replay L248
# @symbol function/class: Closed L259
# @symbol variable/parameter: model_config L262
# @symbol function/class: Credentials L265
# @symbol variable/parameter: alias L268
# @symbol variable/parameter: password L269
# @symbol function/class: Recovery L272
# @symbol variable/parameter: recovery L275
# @symbol function/class: Unlock L278
# @symbol variable/parameter: key L281
# @symbol variable/parameter: salt L282
# @symbol function/class: Activity L285
# @symbol variable/parameter: idle_seconds L288
# @symbol function/class: Delete L291
# @symbol variable/parameter: confirm L295
# @symbol function/class: Settings L298
# @symbol variable/parameter: endpoint L301
# @symbol variable/parameter: model L302
# @symbol variable/parameter: retain_key L304
# @symbol function/class: destination L307
# @symbol variable/parameter: parsed L310
# @symbol variable/parameter: manager L331
# @symbol function/class: public_settings L331
# @symbol variable/parameter: path L333
# @symbol variable/parameter: data L334
# @symbol function/class: Proxy L342
# @symbol variable/parameter: query L366
# @symbol variable/parameter: workspace L367
# @symbol variable/parameter: view L373
# @symbol variable/parameter: db L378
# @symbol variable/parameter: current L389
# @symbol variable/parameter: forwarded L397
# @symbol function/class: create_private_app L419
# @symbol variable/parameter: launcher_token L420
# @symbol variable/parameter: nonce L420
# @symbol variable/parameter: port L420
# @symbol variable/parameter: root L420
# @symbol variable/parameter: ui L420
# @symbol function/class: lifespan L427
# @symbol function/class: idle L430
# @symbol variable/parameter: task L444
# @symbol variable/parameter: app L454
# @symbol variable/parameter: error L466
# @symbol function/class: invalid L466
# @symbol variable/parameter: request L466
# @symbol function/class: bad_value L471
# @symbol function/class: bad_disk L476
# @symbol function/class: identify L485
# @symbol variable/parameter: owner L489
# @symbol function/class: signed L489
# @symbol variable/parameter: response L491
# @symbol function/class: auth_limit L502
# @symbol function/class: health L510
# @symbol function/class: shutdown L521
# @symbol variable/parameter: callback L527
# @symbol function/class: register L534
# @symbol function/class: login L546
# @symbol function/class: reset L555
# @symbol variable/parameter: row L560
# @symbol variable/parameter: fresh L566
# @symbol function/class: account L574
# @symbol variable/parameter: session L576
# @symbol function/class: unlock L584
# @symbol function/class: activity L595
# @symbol function/class: save L603
# @symbol function/class: lock L610
# @symbol function/class: logout L618
# @symbol function/class: delete L630
# @symbol function/class: backup L646
# @symbol variable/parameter: _ L648
# @symbol function/class: get_providers L659
# @symbol function/class: seed L666
# @symbol function/class: providers L681
# @symbol variable/parameter: old L686
# @symbol variable/parameter: config L692
# @index-end
"""Jason Stys: loopback-only real accounts, session-proven vaults, private AI settings and scoped controller.

No public hosting, operator read backdoor, browser executable selection or permissive host execution.
"""

import asyncio
import contextlib
import json
import secrets
import sqlite3
import time
from contextlib import asynccontextmanager
from http.cookies import CookieError, SimpleCookie
from pathlib import Path
from typing import Literal
from urllib.parse import parse_qs, urlparse

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field, model_validator
from starlette.concurrency import run_in_threadpool

from server.accounts import digest, password_matches
from server.ai import CompatibleAdapter, ExtractiveAdapter
from server.private_workspace import Workspaces, atomic_json

CSP = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; worker-src 'self' blob:; img-src 'self' data: blob:; connect-src 'self'; font-src 'self' data:; frame-src 'self' blob:; frame-ancestors 'none'; object-src 'none'; base-uri 'none'; form-action 'self'"
HISTORY_STOP_BYTES = 128 * 1024**2


class Boundary:
    """Validate one literal loopback origin before parsing; authenticate cookies only inside /private."""

    def __init__(self, app, manager: Workspaces, port: int):
        """Bind host/port and isolate cookie names from other local application instances."""
        self.app, self.manager, self.host = app, manager, f"127.0.0.1:{port}"
        self.cookie = f"kbw_account_{port}"
        manager.cookie = self.cookie

    async def __call__(self, scope, receive, send):
        """Bound request bytes and enforce Host, Origin, JSON/CSRF and private ownership before handlers."""
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        raw = scope["headers"]
        headers = {k.decode().lower(): v.decode() for k, v in raw}

        async def guarded(message):
            """Apply privacy/CSP headers even to denials and streamed downloads."""
            if message["type"] == "http.response.start":
                message["headers"] = [
                    (k, v)
                    for k, v in message["headers"]
                    if k.lower()
                    not in {
                        b"content-security-policy",
                        b"cache-control",
                        b"referrer-policy",
                        b"x-frame-options",
                        b"x-content-type-options",
                        b"permissions-policy",
                    }
                ]
                message["headers"] += [
                    (
                        b"content-security-policy",
                        (
                            "sandbox; default-src 'none'; img-src data:; style-src 'unsafe-inline'; frame-ancestors 'self'"
                            if scope["path"].endswith("/preview")
                            else CSP
                        ).encode(),
                    ),
                    (b"cache-control", b"no-store"),
                    (b"referrer-policy", b"no-referrer"),
                    (b"x-content-type-options", b"nosniff"),
                    (
                        b"x-frame-options",
                        b"SAMEORIGIN" if scope["path"].endswith("/preview") else b"DENY",
                    ),
                    (
                        b"permissions-policy",
                        b"camera=(),microphone=(),geolocation=(),payment=(),browsing-topics=()",
                    ),
                ]
            await send(message)

        async def deny(status, detail):
            """Errors are generic and never echo bodies, keys or local data paths."""
            await JSONResponse({"detail": detail}, status)(scope, receive, guarded)

        if (
            headers.get("host") != self.host
            or sum(k.lower() == b"host" for k, _ in raw) != 1
            or scope.get("scheme") != "http"
        ):
            return await deny(403, "Use this application's exact loopback address")
        if (
            headers.get("origin", "http://" + self.host) != "http://" + self.host
            or headers.get("sec-fetch-site") == "cross-site"
        ):
            return await deny(403, "Untrusted origin")
        if not await run_in_threadpool(
            self.manager.accounts.throttle,
            "request:" + str(scope.get("client", ("local",))[0]),
            1000,
        ):
            return await deny(429, "Too many requests; wait before retrying")
        if scope["method"] not in {"GET", "HEAD", "OPTIONS"} and (
            headers.get("x-kbw-request") != "v1"
            or headers.get("content-type", "").split(";")[0]
            not in (
                {"application/json", "multipart/form-data"}
                if scope["path"] == "/private/api/import"
                else {"application/json"}
            )
        ):
            return await deny(403, "Use the app's same-origin JSON request")
        cookies = SimpleCookie()
        try:
            cookies.load(headers.get("cookie", ""))
        except CookieError:
            return await deny(401, "Invalid session")
        token = cookies[self.cookie].value if self.cookie in cookies else ""
        account = await run_in_threadpool(self.manager.accounts.owner, token) if token else None
        scope.setdefault("state", {}).update(account=account, token=token, session=digest(token))
        if (
            scope["path"].startswith("/private/")
            and scope["path"] not in {"/private/login", "/private/register", "/private/reset"}
            and not account
        ):
            return await deny(401, "Sign in to your local account")
        chunks, length = [], 0
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            data = message.get("body", b"")
            length += len(data)
            if length > 4 * 1024**2 + 64000:
                return await deny(413, "Request exceeds 4 MiB")
            chunks.append(data)
            if not message.get("more_body", False):
                break
        delivered = False

        async def replay():
            """Replay bounded bytes once and preserve normal disconnect/file streaming behavior."""
            nonlocal delivered
            if not delivered:
                delivered = True
                return {"type": "http.request", "body": b"".join(chunks), "more_body": False}
            return await receive()

        await self.app(scope, replay, guarded)


class Closed(BaseModel):
    """Unknown fields never grant owner, filesystem or execution privileges."""

    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class Credentials(Closed):
    """Non-identifying lower-case alias; a long bounded login password."""

    alias: str = Field(pattern=r"^[a-z0-9_][a-z0-9_-]{2,39}$")
    password: str = Field(min_length=15, max_length=128)


class Recovery(Credentials):
    """One-use login recovery is independent of the irreversible vault phrase."""

    recovery: str = Field(min_length=32, max_length=128)


class Unlock(Closed):
    """Browser-derived key is used in the trusted service only while this account is unlocked."""

    key: str = Field(min_length=44, max_length=44)
    salt: str | None = Field(default=None, min_length=24, max_length=24)


class Activity(Closed):
    """Only intentional human activity renews idle timeout; passive polling does not."""

    idle_seconds: Literal[600, 1800, 7200] = 600


class Delete(Closed):
    """Current-password/explicit confirmation gates removal of this account only."""

    password: str = Field(min_length=15, max_length=128)
    confirm: Literal[True]


class Settings(Closed):
    """Own explicitly selected model endpoint; no arbitrary imports or hidden global keys."""

    endpoint: str = Field(default="", max_length=2048)
    model: str = Field(default="local-model", min_length=1, max_length=128)
    key: str = Field(default="", max_length=4096)
    retain_key: bool = False

    @model_validator(mode="after")
    def destination(self):
        """Permit the official HTTPS chat endpoint or literal IPv4 loopback model servers."""
        if self.endpoint:
            parsed = urlparse(self.endpoint)
            if not (
                self.endpoint == "https://api.openai.com/v1/chat/completions"
                or (
                    parsed.scheme == "http"
                    and parsed.hostname == "127.0.0.1"
                    and parsed.port
                    and 1024 <= parsed.port <= 65535
                    and parsed.path == "/v1/chat/completions"
                    and not parsed.username
                    and not parsed.password
                    and not parsed.query
                    and not parsed.fragment
                )
            ):
                raise ValueError(
                    "Use the official HTTPS endpoint or a literal loopback compatible server"
                )
        return self


def public_settings(manager):
    """Show own destination, model and key availability, never plaintext credentials."""
    path = manager.active / "provider.private.json"
    data = (
        json.loads(path.read_text())
        if path.exists()
        else {"endpoint": "", "model": "local-model", "revision": "offline"}
    )
    return {k: v for k, v in data.items() if k != "key"} | {"has_key": bool(data.get("key"))}


class Proxy:
    """Inject a trusted own-account identity into the preserved engine only after session-specific key proof."""

    def __init__(self, manager: Workspaces):
        """Bind one exclusive, mutable account coordinator—not caller-selected filesystem roots."""
        self.manager = manager

    async def __call__(self, scope, receive, send):
        """Authorize every document/download/AI call and serialize it against locking, consent and storage budgets."""
        if scope["type"] != "http":
            return
        manager = self.manager
        async with manager.requests:
            try:
                app = manager.require(scope["state"]["account"]["id"], scope["state"]["session"])
            except ValueError:
                return await JSONResponse({"detail": "Unlock this session's workspace first"}, 423)(
                    scope, receive, send
                )
            path = scope["path"].removeprefix("/private/api")
            if path in {"/login", "/logout"}:
                return await JSONResponse({"detail": "Use private account controls"}, 403)(
                    scope, receive, send
                )
            query = parse_qs(scope.get("query_string", b"").decode())
            workspace = query.get("workspace", ["industrial"])[0]
            if workspace not in {"industrial", "renewable", "laboratory"}:
                return await JSONResponse({"detail": "Unknown own workspace"}, 422)(
                    scope, receive, send
                )
            headers = {k.lower(): v for k, v in scope["headers"]}
            view = headers.get(b"x-kbw-view", b"admin").decode()
            if view not in {"admin", "employee", "customer", "visitor"}:
                return await JSONResponse({"detail": "Unknown preview role"}, 422)(
                    scope, receive, send
                )
            db = manager.active / "workbench.sqlite"
            if (
                scope["method"] in {"POST", "PUT"}
                and path in {"/import", "/products", "/merge"}
                and db.stat().st_size >= HISTORY_STOP_BYTES
            ):
                return await JSONResponse(
                    {"detail": "Workspace capacity reached; reads and exports remain available"},
                    409,
                )(scope, receive, send)
            if path == "/ask" or "/vision/" in path:
                current = public_settings(manager)
                if (
                    current["endpoint"]
                    and headers.get(b"x-kbw-provider-revision", b"").decode() != current["revision"]
                ):
                    return await JSONResponse(
                        {"detail": "Review the AI destination and renew source consent"}, 409
                    )(scope, receive, send)
            forwarded = dict(scope, path="/api" + path, root_path="")
            forwarded["state"] = dict(
                scope["state"],
                private_user={
                    "username": scope["state"]["account"]["username"],
                    "workspace": workspace,
                    "role": "customer" if view == "visitor" else view,
                    "customer": headers.get(b"x-kbw-customer", b"north").decode(),
                    "csrf": "internal-only",
                    "visitor": view == "visitor",
                },
            )
            forwarded["headers"] = [
                (k, v) for k, v in scope["headers"] if k.lower() != b"x-csrf-token"
            ] + [(b"x-csrf-token", b"internal-only")]
            await app(forwarded, receive, send)
            try:
                await run_in_threadpool(manager.save)
            except (OSError, ValueError):
                manager.failed = True


def create_private_app(
    root: Path, port: int, ui: Path | None = None, launcher_token: str = "", nonce: str = ""
):
    """Construct local account lifecycle; document conversion and AI stay explicit and account-private."""
    manager = Workspaces(root)
    manager.last_human, manager.idle_seconds = time.monotonic(), 600

    @asynccontextmanager
    async def lifespan(app):
        """Bound idle snapshots and clean only owned jobs/workspaces on normal shutdown."""

        async def idle():
            """Background polling does not renew keys; snapshots wait for terminal jobs."""
            while True:
                await asyncio.sleep(5)
                async with manager.requests:
                    if manager.owner:
                        try:
                            if time.monotonic() - manager.last_human > manager.idle_seconds:
                                await manager.lock(manager.owner)
                            else:
                                await run_in_threadpool(manager.save)
                        except (OSError, ValueError, sqlite3.Error):
                            manager.failed = True

        task = asyncio.create_task(idle())
        try:
            yield
        finally:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task
            async with manager.requests:
                await manager.close()

    app = FastAPI(
        title="Business Knowledge Workbench — Jason Stys",
        version="1.1.1",
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    app.state.manager = manager
    app.add_middleware(Boundary, manager=manager, port=port)

    @app.exception_handler(RequestValidationError)
    async def invalid(request, error):
        """Never echo passwords, keys, source bodies or provider secrets from validation errors."""
        return JSONResponse({"detail": "Invalid fields; check the documented sizes/formats"}, 422)

    @app.exception_handler(ValueError)
    async def bad_value(request, error):
        """Return bounded authored errors, not arbitrary exception/SQL contents."""
        return JSONResponse({"detail": str(error)[:250]}, 400)

    @app.exception_handler(OSError)
    async def bad_disk(request, error):
        """A failed save preserves active recovery data and does not expose private paths."""
        return JSONResponse(
            {
                "detail": "Local storage operation failed; preserve recovery data and free disk space"
            },
            400,
        )

    def identify(request):
        """Trust only the boundary's authenticated cookie identity, never body owner IDs."""
        return request.state.account["id"], request.state.session

    def signed(owner, data):
        """Issue a high-entropy HttpOnly local cookie; stored sessions contain only its digest."""
        response = JSONResponse(data)
        response.set_cookie(
            manager.cookie,
            manager.accounts.session(owner),
            httponly=True,
            samesite="strict",
            max_age=8 * 3600,
            path="/private",
        )
        return response

    async def auth_limit(alias):
        """Persist global/alias auth throttles without logging submitted secrets."""
        if not await run_in_threadpool(
            manager.accounts.throttle, "auth", 40
        ) or not await run_in_threadpool(manager.accounts.throttle, "alias:" + alias, 10):
            raise HTTPException(429, "Too many attempts; wait five minutes")

    @app.get("/health")
    def health():
        """Public ready metadata/launch correlation is not an authorization token."""
        return {
            "status": "ready",
            "mode": "private-local-accounts",
            "version": "1.1.1",
            "author": "Jason Stys",
            "launcher_nonce": nonce,
        }

    @app.post("/launcher/shutdown")
    def shutdown(request: Request):
        """Only an optional process-local native-launch secret can stop this service; never passed to the renderer."""
        if not launcher_token or not secrets.compare_digest(
            request.headers.get("authorization", ""), "Bearer " + launcher_token
        ):
            raise HTTPException(403, "Launcher authorization required")
        callback = getattr(app.state, "shutdown", None)
        if callback is None:
            raise HTTPException(409, "Launcher shutdown is unavailable")
        callback()
        return {"stopping": True}

    @app.post("/private/register")
    async def register(data: Credentials):
        """Create empty real accounts and show a random recovery code once, with no seeded/demo passwords."""
        await auth_limit(data.alias)
        try:
            owner, recovery = await run_in_threadpool(
                manager.accounts.register, data.alias, data.password
            )
        except sqlite3.IntegrityError:
            raise HTTPException(409, "Alias unavailable") from None
        return signed(owner, {"recovery": recovery})

    @app.post("/private/login")
    async def login(data: Credentials):
        """Authenticate a password without unlocking its independent source vault."""
        await auth_limit(data.alias)
        owner = await run_in_threadpool(manager.accounts.login, data.alias, data.password)
        if not owner:
            raise HTTPException(401, "Alias or password is incorrect")
        return signed(owner, {"signed_in": True})

    @app.post("/private/reset")
    async def reset(data: Recovery):
        """Seal before consuming a valid recovery code; storage failure must not lose the replacement code."""
        await auth_limit(data.alias)
        async with manager.requests:
            with manager.accounts.connection() as db:
                row = db.execute(
                    "SELECT id,recovery FROM accounts WHERE username=?", (data.alias,)
                ).fetchone()
            if not row or not secrets.compare_digest(row["recovery"], digest(data.recovery)):
                raise HTTPException(401, "Recovery credentials invalid")
            await manager.lock(row["id"])
            fresh = await run_in_threadpool(
                manager.accounts.reset, data.alias, data.recovery, data.password
            )
            if not fresh:
                raise HTTPException(409, "Recovery credentials changed")
            return {"recovery": fresh}

    @app.get("/private/account")
    def account(request: Request):
        """Return caller-only state; login-only sessions cannot see already-unlocked code."""
        owner, session = identify(request)
        return {
            "alias": request.state.account["username"],
            **manager.status(owner, session),
            "idle_seconds": manager.idle_seconds,
        }

    @app.post("/private/unlock")
    async def unlock(request: Request, data: Unlock):
        """Prove this session's key and intentionally reset the human-idle clock."""
        owner, session = identify(request)
        if not await run_in_threadpool(manager.accounts.throttle, "unlock:" + owner, 10):
            raise HTTPException(429, "Too many unlock attempts; wait five minutes")
        async with manager.requests:
            await manager.unlock(owner, session, data.key, data.salt)
            manager.last_human, manager.idle_seconds = time.monotonic(), 600
            return manager.status(owner, session)

    @app.post("/private/activity")
    async def activity(request: Request, data: Activity):
        """Only a vault-proven session can choose/renew human-idle timeout."""
        async with manager.requests:
            manager.require(*identify(request))
            manager.last_human, manager.idle_seconds = time.monotonic(), data.idle_seconds
            return {"idle_seconds": data.idle_seconds}

    @app.post("/private/save")
    async def save(request: Request):
        """Explicit complete encrypted backup requires no active compiler jobs."""
        async with manager.requests:
            manager.require(*identify(request))
            return await run_in_threadpool(manager.save, True)

    @app.post("/private/lock")
    async def lock(request: Request):
        """Cancel/clean this account's jobs, seal and drop active source/key; recovery stays on failure."""
        async with manager.requests:
            owner, session = identify(request)
            manager.require(owner, session)
            return await manager.lock(owner)

    @app.post("/private/logout")
    async def logout(request: Request):
        """Seal a proven account or revoke an unproven login; never cancel another account's jobs."""
        async with manager.requests:
            owner, session = identify(request)
            if manager.owner == owner and session in manager.sessions:
                await manager.lock(owner)
            await run_in_threadpool(manager.accounts.revoke, request.state.token)
        response = JSONResponse({"signed_out": True})
        response.delete_cookie(manager.cookie, path="/private")
        return response

    @app.post("/private/delete")
    async def delete(request: Request, data: Delete):
        """Require current password and confirmation; delete only this account and its live archive."""
        async with manager.requests:
            owner, _ = identify(request)
            with manager.accounts.connection() as db:
                row = db.execute("SELECT password FROM accounts WHERE id=?", (owner,)).fetchone()
            if not row or not await run_in_threadpool(password_matches, data.password, row[0]):
                raise HTTPException(401, "Current password incorrect")
            await manager.delete(owner)
            if not await run_in_threadpool(manager.accounts.delete, owner, data.password):
                raise HTTPException(409, "Account changed; sign in again")
        response = JSONResponse({"deleted": True})
        response.delete_cookie(manager.cookie, path="/private")
        return response

    @app.get("/private/backup")
    def backup(request: Request):
        """Download only this owner's encrypted archive; cold root backup also needs its account/key settings."""
        owner, _ = identify(request)
        path = manager.archive(owner)
        if not path.exists():
            raise HTTPException(404, "Save an encrypted snapshot first")
        return FileResponse(
            path,
            media_type="application/octet-stream",
            filename="business-knowledge-encrypted.kbwvault",
        )

    @app.get("/private/providers")
    async def get_providers(request: Request):
        """Return own selected endpoint and whether a credential exists."""
        async with manager.requests:
            manager.require(*identify(request))
            return public_settings(manager)

    @app.post("/private/seed")
    async def seed(request: Request):
        """Explicit own-account synthetic sample import; never creates demo users or overwrites records."""
        from server.store import connect, initialize

        async with manager.requests:
            manager.require(*identify(request))
            path = manager.active / "workbench.sqlite"
            await run_in_threadpool(initialize, path, False, True)
            with connect(path) as db:
                db.execute("DELETE FROM sessions")
                db.execute("DELETE FROM users")
            await run_in_threadpool(manager.save, True)
            return {"seeded": True}

    @app.put("/private/providers")
    async def providers(request: Request, data: Settings):
        """Store only this account's explicit key/endpoint inside its encrypted workspace."""
        async with manager.requests:
            manager.require(*identify(request))
            path = manager.active / "provider.private.json"
            old = json.loads(path.read_text()) if path.exists() else {}
            key = data.key
            if data.retain_key and not key:
                if old.get("endpoint") != data.endpoint:
                    raise ValueError("Changed destination needs a newly entered key")
                key = old.get("key", "")
            config = {
                "endpoint": data.endpoint,
                "model": data.model,
                "key": key,
                "revision": secrets.token_hex(16),
            }
            await run_in_threadpool(atomic_json, path, config)
            manager.app.state.ai_adapter = (
                CompatibleAdapter(data.endpoint, data.model, key)
                if data.endpoint
                else ExtractiveAdapter()
            )
            await run_in_threadpool(manager.save, True)
            return public_settings(manager)

    app.mount("/private/api", Proxy(manager))
    if ui and ui.exists():
        app.mount("/", StaticFiles(directory=ui, html=True))
    return app
