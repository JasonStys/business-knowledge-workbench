# @index-begin
# @symbol variable/parameter: ROOT L190
# @symbol variable/parameter: CONVERSION_SLOTS L191
# @symbol variable/parameter: config L194
# @symbol function/class: convert_payload L194
# @symbol variable/parameter: data L194
# @symbol variable/parameter: name L194
# @symbol variable/parameter: worker_env L206
# @symbol variable/parameter: key L208
# @symbol variable/parameter: value L208
# @symbol variable/parameter: command L211
# @symbol variable/parameter: converted L216
# @symbol variable/parameter: payload L226
# @symbol function/class: BodyLimit L238
# @symbol function/class: __init__ L241
# @symbol variable/parameter: self L241
# @symbol function/class: __call__ L245
# @symbol variable/parameter: receive L245
# @symbol variable/parameter: scope L245
# @symbol variable/parameter: send L245
# @symbol variable/parameter: chunks L249
# @symbol variable/parameter: total L250
# @symbol variable/parameter: message L252
# @symbol function/class: replay L264
# @symbol function/class: create_app L271
# @symbol variable/parameter: demo L272
# @symbol variable/parameter: path L272
# @symbol variable/parameter: private_mode L272
# @symbol variable/parameter: database_path L275
# @symbol variable/parameter: secure L277
# @symbol variable/parameter: ai_adapter L279
# @symbol variable/parameter: login_attempts L280
# @symbol variable/parameter: attempts_lock L281
# @symbol variable/parameter: application L284
# @symbol function/class: lifespan L284
# @symbol variable/parameter: call_next L293
# @symbol variable/parameter: request L293
# @symbol function/class: security_headers L293
# @symbol variable/parameter: origin L295
# @symbol variable/parameter: allowed L296
# @symbol variable/parameter: response L304
# @symbol function/class: current L319
# @symbol variable/parameter: required L319
# @symbol variable/parameter: token L328
# @symbol variable/parameter: user L334
# @symbol function/class: authorize L339
# @symbol variable/parameter: mutate L339
# @symbol variable/parameter: roles L339
# @symbol function/class: configuration L350
# @symbol variable/parameter: workspace L350
# @symbol variable/parameter: database L360
# @symbol function/class: ensure_revision L360
# @symbol variable/parameter: active L362
# @symbol function/class: accessible L370
# @symbol variable/parameter: identifier L370
# @symbol variable/parameter: predicate L376
# @symbol variable/parameter: values L376
# @symbol function/class: health L386
# @symbol function/class: bootstrap L393
# @symbol variable/parameter: configs L396
# @symbol function/class: staff_options L419
# @symbol function/class: add_product L425
# @symbol variable/parameter: body L425
# @symbol variable/parameter: text L431
# @symbol function/class: login L471
# @symbol variable/parameter: address L475
# @symbol variable/parameter: now L476
# @symbol variable/parameter: recent L480
# @symbol variable/parameter: stamp L480
# @symbol variable/parameter: encoded L490
# @symbol variable/parameter: valid L491
# @symbol variable/parameter: csrf L494
# @symbol function/class: session L514
# @symbol function/class: logout L522
# @symbol function/class: products L535
# @symbol variable/parameter: q L536
# @symbol function/class: list_documents L560
# @symbol variable/parameter: category L564
# @symbol variable/parameter: sort L565
# @symbol variable/parameter: filters L579
# @symbol function/class: library L579
# @symbol function/class: document L587
# @symbol variable/parameter: _ L589
# @symbol function/class: document_preview L593
# @symbol function/class: export L605
# @symbol variable/parameter: format_name L605
# @symbol function/class: source L628
# @symbol variable/parameter: suffix L633
# @symbol function/class: upload L641
# @symbol variable/parameter: file L643
# @symbol variable/parameter: visibility L644
# @symbol variable/parameter: customer L645
# @symbol variable/parameter: dataset L647
# @symbol variable/parameter: digest L667
# @symbol variable/parameter: scope_customer L668
# @symbol variable/parameter: existing L670
# @symbol variable/parameter: result L691
# @symbol variable/parameter: tables L728
# @symbol variable/parameter: block L730
# @symbol variable/parameter: headers L738
# @symbol variable/parameter: alias L739
# @symbol variable/parameter: mapped L741
# @symbol variable/parameter: record L745
# @symbol variable/parameter: product L755
# @symbol function/class: merge L796
# @symbol variable/parameter: sources L801
# @symbol variable/parameter: source_row L804
# @symbol variable/parameter: provenance L813
# @symbol function/class: get_config L845
# @symbol function/class: save_config L855
# @symbol variable/parameter: previous L862
# @symbol variable/parameter: used L879
# @symbol function/class: preview_standard L904
# @symbol function/class: preview_file L915
# @symbol variable/parameter: draft L921
# @symbol function/class: standard_history L929
# @symbol function/class: restore_standard L947
# @symbol variable/parameter: restored L957
# @symbol function/class: standardize_document L962
# @symbol variable/parameter: old L970
# @symbol variable/parameter: copied L973
# @symbol variable/parameter: warnings L996
# @symbol variable/parameter: new_id L1011
# @symbol function/class: sales_report L1038
# @symbol function/class: export_report L1053
# @symbol variable/parameter: rows L1061
# @symbol variable/parameter: blocks L1065
# @symbol function/class: measurement L1094
# @symbol function/class: audit_log L1102
# @symbol function/class: context_for L1114
# @symbol variable/parameter: context L1118
# @symbol variable/parameter: budget L1119
# @symbol variable/parameter: row L1120
# @symbol function/class: ask L1137
# @symbol variable/parameter: index L1149
# @symbol function/class: vision L1149
# @symbol variable/parameter: app L1177
# @index-end
"""Same-origin application, authentication, role gates and API orchestration. Index: docs/code-index.md.

Cookie sessions use CSRF tokens; all document, data and AI operations enforce workspace/customer ACLs.
"""

import hashlib
import json
import os
import re
import secrets
import subprocess
import sys
import threading
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from .ai import adapter, validate_answer
from .analytics import report
from .conversion import MAX_BYTES, SUPPORTED, ingest, render_document
from .exports import FORMATS, export_document
from .library import LibraryQuery
from .library import search as search_library
from .models import (
    Login,
    MeasurementRequest,
    MergeRequest,
    ProductRequest,
    Question,
    StandardPreview,
    StandardRestore,
    WorkspaceConfig,
)
from .standards import identity
from .store import (
    SCENARIOS,
    acl,
    audit,
    connect,
    documents,
    initialize,
    password_hash,
    verify_password,
)
from .units import UNITS, convert

ROOT = Path(__file__).resolve().parent.parent
CONVERSION_SLOTS = threading.BoundedSemaphore(2)


def convert_payload(name: str, data: bytes, config: WorkspaceConfig) -> dict:
    """Share the timed, credential-stripped worker for actual imports and unsaved file previews."""
    if (
        not re.fullmatch(r"[\w .()\-]{1,100}\.[A-Za-z0-9]{1,8}", name)
        or name.rsplit(".", 1)[-1].lower() not in SUPPORTED
    ):
        raise HTTPException(415, "Unsupported format or unsafe filename")
    if not data or len(data) > MAX_BYTES:
        raise HTTPException(413, "Source must be 1 byte to 4 MiB")
    if not CONVERSION_SLOTS.acquire(blocking=False):
        raise HTTPException(429, "Conversion workers busy; retry later")
    try:
        worker_env = {
            key: value
            for key, value in os.environ.items()
            if key in {"PATH", "SystemRoot", "SYSTEMROOT", "TEMP", "TMP", "LANG"}
        }
        command = (
            [sys.executable, "--convert"]
            if getattr(sys, "frozen", False)
            else [sys.executable, "-m", "server.worker"]
        )
        converted = subprocess.run(
            [*command, name, config.model_dump_json()],
            input=data,
            capture_output=True,
            timeout=25,
            cwd=ROOT,
            env=worker_env,
            check=False,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        payload = json.loads(converted.stdout)
        if converted.returncode or "result" not in payload:
            raise ValueError("Source rejected")
        return payload["result"]
    except (ValueError, subprocess.TimeoutExpired) as error:
        raise HTTPException(
            422, "Conversion rejected: corrupt, unsafe, unsupported or over-budget file"
        ) from error
    finally:
        CONVERSION_SLOTS.release()


class BodyLimit:
    """ASGI boundary: bound request bodies before multipart parsing or disk spooling."""

    def __init__(self, app):
        """Wrap the downstream ASGI application."""
        self.app = app

    async def __call__(self, scope, receive, send):
        """Buffer at most five MiB, reject oversized bodies, then replay bounded messages."""
        if scope["type"] != "http" or scope["method"] not in {"POST", "PUT", "PATCH"}:
            return await self.app(scope, receive, send)
        chunks = []
        total = 0
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            total += len(message.get("body", b""))
            if total > MAX_BYTES + 64_000:
                return await JSONResponse(
                    {"detail": "Request body exceeds limit"}, status_code=413
                )(scope, receive, send)
            chunks.append(message)
            if not message.get("more_body", False):
                break

        async def replay():
            """Replay original bounded ASGI messages in order."""
            return chunks.pop(0) if chunks else await receive()

        await self.app(scope, replay, send)


def create_app(
    path: Path | None = None, demo: bool | None = None, private_mode: bool = False
) -> FastAPI:
    """Application factory supports isolated test databases and explicit demo enrollment."""
    database_path = path or Path(os.environ.get("KB_DB", ROOT / "data/workbench.sqlite"))
    demo = os.environ.get("KB_DEMO", "0") == "1" if demo is None else demo
    secure = os.environ.get("KB_SECURE_COOKIE", "0" if demo else "1") == "1"
    initialize(database_path, demo)
    ai_adapter = adapter() if not private_mode else None
    login_attempts: dict[str, list[float]] = {}
    attempts_lock = threading.Lock()

    @asynccontextmanager
    async def lifespan(application):
        """Keep application lifecycle explicit for hosting and browser tests."""
        yield

    app = FastAPI(title="Business Knowledge Workbench", version="1.0.0", lifespan=lifespan)
    app.state.ai_adapter = ai_adapter
    app.add_middleware(BodyLimit)

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        """Enforce same-origin writes and prevent private response caching or active embedding."""
        origin = request.headers.get("origin")
        allowed = os.environ.get("KB_ORIGIN", "http://127.0.0.1:8000")
        if (
            request.method in {"POST", "PUT", "PATCH", "DELETE"}
            and origin
            and not private_mode
            and origin not in {allowed, "http://127.0.0.1:5173" if demo else allowed}
        ):
            return JSONResponse({"detail": "Origin not allowed"}, status_code=403)
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        response.headers.setdefault(
            "Content-Security-Policy",
            (
                "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-src 'self' blob:; object-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'self'"
            ),
        )
        return response

    def current(request: Request, required: bool = True) -> dict | None:
        """Resolve a hashed, expiring opaque session; never accept roles from request data."""
        if private_mode:
            user = getattr(request.state, "private_user", None)
            if user and user.get("visitor"):
                user = None
            if required and not user:
                raise HTTPException(401, "Sign in required")
            return user
        token = request.cookies.get("kb_session", "")
        with connect(database_path) as database:
            row = database.execute(
                "SELECT users.*,sessions.csrf FROM sessions JOIN users ON users.id=sessions.user_id WHERE sessions.token=? AND expires>?",
                (hashlib.sha256(token.encode()).hexdigest(), time.time()),
            ).fetchone()
        user = dict(row) if row else None
        if required and not user:
            raise HTTPException(401, "Sign in required")
        return user

    def authorize(request: Request, roles: set[str] | None = None, mutate: bool = False) -> dict:
        """Check role and CSRF independently of any front-end view selection."""
        user = current(request)
        if roles and user["role"] not in roles:
            raise HTTPException(403, "Role not allowed")
        if mutate and not secrets.compare_digest(
            request.headers.get("x-csrf-token", ""), user["csrf"]
        ):
            raise HTTPException(403, "CSRF token required")
        return user

    def configuration(workspace: str) -> WorkspaceConfig:
        """Load a validated active workspace configuration."""
        with connect(database_path) as database:
            row = database.execute(
                "SELECT config FROM workspaces WHERE id=?", (workspace,)
            ).fetchone()
        if not row:
            raise HTTPException(404, "Workspace not found")
        return WorkspaceConfig.model_validate_json(row["config"])

    def ensure_revision(database, workspace: str, config: WorkspaceConfig):
        """A write transaction must still match the standard read before potentially slow work."""
        active = WorkspaceConfig.model_validate_json(
            database.execute("SELECT config FROM workspaces WHERE id=?", (workspace,)).fetchone()[0]
        )
        if active.revision != config.revision:
            raise HTTPException(
                409, "Standard changed during conversion; retry with the current revision"
            )

    def accessible(request: Request, identifier: str) -> tuple[dict, dict | None]:
        """Fetch one document using the session's scope, returning 404 for unauthorized IDs."""
        user = current(request, False)
        workspace = (
            user["workspace"] if user else request.query_params.get("workspace", "industrial")
        )
        predicate, values = acl(user, workspace)
        with connect(database_path) as database:
            row = database.execute(
                "SELECT * FROM documents WHERE id=? AND " + predicate, [identifier, *values]
            ).fetchone()
        if not row:
            raise HTTPException(404, "Document not found")
        return dict(row), user

    @app.get("/api/health")
    def health():
        """Report database connectivity without leaking private records."""
        with connect(database_path) as database:
            database.execute("SELECT 1")
        return {"status": "ok", "schema_version": 1}

    @app.get("/api/bootstrap")
    def bootstrap():
        """Expose public capabilities and synthetic scenario descriptions, never credentials."""
        with connect(database_path) as database:
            configs = [
                WorkspaceConfig.model_validate_json(row[0])
                for row in database.execute("SELECT config FROM workspaces ORDER BY id")
            ]
        return {
            "workspaces": [
                {
                    "id": config.profile,
                    "title": config.title,
                    "context": SCENARIOS.get(config.profile, {}).get(
                        "context",
                        "A configurable business workspace for structured documentation, product information and performance records.",
                    ),
                }
                for config in configs
            ],
            "formats": SUPPORTED,
            "exports": list(FORMATS),
            "units": UNITS,
            "demo": demo,
        }

    @app.get("/api/options")
    def staff_options(request: Request):
        """Expose account labels to authorized staff, never the public catalog."""
        user = authorize(request, {"employee", "admin"})
        return {"customers": configuration(user["workspace"]).customers}

    @app.post("/api/products")
    def add_product(body: ProductRequest, request: Request):
        """Create a catalog/assigned-inventory entry and its canonical public specification."""
        user = authorize(request, {"employee", "admin"}, mutate=True)
        config = configuration(user["workspace"])
        if body.customer not in config.customers:
            raise HTTPException(422, "Customer must match a configured account")
        text = body.name + ". " + body.description + "\n\n" + body.specifications
        try:
            result = ingest(body.id + "-specification.txt", text.encode(), config)
        except ValueError as error:
            raise HTTPException(422, "Invalid product specifications") from error
        with connect(database_path) as database:
            if database.execute(
                "SELECT 1 FROM products WHERE workspace=? AND id=?", (user["workspace"], body.id)
            ).fetchone():
                raise HTTPException(409, "Product ID already exists")
            database.execute(
                "INSERT INTO products VALUES (?,?,?,?,?,?,?,?)",
                (
                    body.id,
                    user["workspace"],
                    body.name,
                    body.category,
                    body.description,
                    body.price_cents,
                    body.customer,
                    json.dumps(result["measurements"]),
                ),
            )
            identifier = str(uuid.uuid4())
            database.execute(
                "INSERT INTO documents(id,workspace,title,visibility,product,category,result,source,source_hash) VALUES (?,?,?,'public',?,'Overview',?,?,?)",
                (
                    identifier,
                    user["workspace"],
                    result["title"],
                    body.id,
                    json.dumps(result),
                    text.encode(),
                    result["provenance"]["sha256"],
                ),
            )
            audit(database, user, "create-product", body.id)
        return {"id": body.id, "document_id": identifier}

    @app.post("/api/login")
    def login(body: Login, request: Request):
        """Rate-limit login, verify credentials, and create an expiring opaque cookie session."""
        if private_mode:
            raise HTTPException(403, "Use private account login")
        address = request.client.host if request.client else "unknown"
        now = time.monotonic()
        with attempts_lock:
            if len(login_attempts) > 1000:
                login_attempts.clear()
            recent = [stamp for stamp in login_attempts.get(address, []) if now - stamp < 60]
            if len(recent) >= min(100, max(10, int(os.environ.get("KB_LOGIN_LIMIT", "10")))):
                raise HTTPException(429, "Too many login attempts; retry after one minute")
            login_attempts[address] = [*recent, now]
        with connect(database_path) as database:
            user = database.execute(
                "SELECT * FROM users WHERE workspace=? AND username=?",
                (body.workspace, body.username),
            ).fetchone()
            # Equalize password hashing work for unknown accounts.
            encoded = user["password"] if user else password_hash("not-a-real-account", "0" * 32)
            valid = verify_password(body.password, encoded)
            if not user or not valid:
                raise HTTPException(401, "Invalid credentials")
            token, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
            database.execute("DELETE FROM sessions WHERE expires<?", (time.time(),))
            database.execute(
                "INSERT INTO sessions VALUES (?,?,?,?)",
                (hashlib.sha256(token.encode()).hexdigest(), user["id"], csrf, time.time() + 3600),
            )
        response = JSONResponse(
            {
                "username": user["username"],
                "role": user["role"],
                "workspace": user["workspace"],
                "csrf": csrf,
            }
        )
        response.set_cookie(
            "kb_session", token, httponly=True, secure=secure, samesite="strict", max_age=3600
        )
        return response

    @app.get("/api/session")
    def session(request: Request):
        """Restore signed-in browser state without exposing session or password hashes."""
        user = current(request, False)
        return (
            {key: user[key] for key in ["username", "role", "workspace", "csrf"]} if user else None
        )

    @app.post("/api/logout")
    def logout(request: Request):
        """Invalidate the server session and clear its browser cookie."""
        authorize(request, mutate=True)
        with connect(database_path) as database:
            database.execute(
                "DELETE FROM sessions WHERE token=?",
                (hashlib.sha256(request.cookies.get("kb_session", "").encode()).hexdigest(),),
            )
        response = JSONResponse({"status": "signed-out"})
        response.delete_cookie("kb_session")
        return response

    @app.get("/api/products")
    def products(
        request: Request, workspace: str = "industrial", q: str = Query("", max_length=120)
    ):
        """Public catalog or scoped customer inventory; no customer ownership metadata leaks."""
        user = current(request, False)
        if user:
            workspace = user["workspace"]
        with connect(database_path) as database:
            predicate, values = "workspace=?", [workspace]
            if user and user["role"] == "customer":
                predicate += " AND customer=?"
                values.append(user["customer"])
            rows = database.execute(
                "SELECT id,name,category,description,price_cents,specifications FROM products WHERE "
                + predicate
                + " ORDER BY name",
                values,
            ).fetchall()
        return [
            dict(row) | {"specifications": json.loads(row["specifications"])}
            for row in rows
            if q.casefold() in (row["id"] + row["name"] + row["description"]).casefold()
        ]

    @app.get("/api/documents")
    def list_documents(
        request: Request,
        workspace: str = "industrial",
        q: str = Query("", max_length=120),
        category: str = Query("", max_length=40),
        sort: str = Query("title", pattern="^(title|newest|category)$"),
    ):
        """Filter and reorder document metadata after ACL enforcement."""
        user = current(request, False)
        workspace = user["workspace"] if user else workspace
        with connect(database_path) as database:
            rows = documents(database, user, workspace, q, category, sort)
        return [
            {key: value for key, value in row.items() if key not in {"result", "customer"}}
            | {"review_status": json.loads(row["result"])["review_status"]}
            for row in rows
        ]

    @app.get("/api/library")
    def library(request: Request, filters: LibraryQuery = Query()):
        """Return authorized, paged standardized-file metadata, content matches and scoped facets."""
        user = current(request, False)
        workspace = user["workspace"] if user else filters.workspace
        with connect(database_path) as database:
            return search_library(database, user, workspace, filters)

    @app.get("/api/documents/{identifier}")
    def document(request: Request, identifier: str):
        """Return authorized semantic content and provenance for human or machine consumption."""
        row, _ = accessible(request, identifier)
        return json.loads(row["result"])

    @app.get("/api/documents/{identifier}/preview")
    def document_preview(request: Request, identifier: str):
        """Serve sanitized canonical HTML for a scriptless same-origin frame; never raw uploads."""
        row, _ = accessible(request, identifier)
        return Response(
            json.loads(row["result"])["html"],
            media_type="text/html",
            headers={
                "Content-Security-Policy": "sandbox; default-src 'none'; img-src data:; style-src 'unsafe-inline'; frame-ancestors 'self'"
            },
        )

    @app.get("/api/documents/{identifier}/export/{format_name}")
    def export(request: Request, identifier: str, format_name: str):
        """Download a conversion generated from persisted canonical HTML."""
        if format_name not in FORMATS:
            raise HTTPException(400, "Unsupported export format")
        row, _ = accessible(request, identifier)
        try:
            payload = export_document(json.loads(row["result"]), format_name)
        except ValueError as error:
            raise HTTPException(422, str(error)) from error
        response = Response(
            payload,
            media_type=FORMATS[format_name],
            headers={
                "Content-Disposition": f'attachment; filename="document-{identifier[:80]}.{format_name}"'
            },
        )
        if format_name == "html":
            response.headers["Content-Security-Policy"] = (
                "sandbox; default-src 'none'; img-src data:; style-src 'unsafe-inline'"
            )
        return response

    @app.get("/api/documents/{identifier}/source")
    def source(request: Request, identifier: str):
        """Retain original evidence as attachment only, never execute or render raw uploads."""
        row, _ = accessible(request, identifier)
        if row["source"] is None:
            raise HTTPException(404, "Compilation has no single original source")
        suffix = json.loads(row["result"])["provenance"]["source_name"].rsplit(".", 1)[-1].lower()
        return Response(
            row["source"],
            media_type="application/octet-stream",
            headers={"Content-Disposition": f'attachment; filename="source.{suffix}"'},
        )

    @app.post("/api/import")
    def upload(
        request: Request,
        file: UploadFile = File(),
        visibility: str = Form("internal"),
        customer: str = Form("north"),
        category: str = Form("Imported"),
        dataset: bool = Form(False),
    ):
        """Convert in a timed credential-free worker; atomically persist document and optional sales."""
        user = authorize(request, {"employee", "admin"}, mutate=True)
        config = configuration(user["workspace"])
        if (
            visibility not in {"public", "customer", "internal"}
            or customer not in config.customers
            or not 1 <= len(category) <= 40
        ):
            raise HTTPException(422, "Invalid visibility, customer or category")
        name = file.filename or ""
        if (
            not re.fullmatch(r"[\w .()\-]{1,100}\.[A-Za-z0-9]{1,8}", name)
            or name.rsplit(".", 1)[-1].lower() not in SUPPORTED
        ):
            raise HTTPException(415, "Unsupported format or unsafe filename")
        data = file.file.read(MAX_BYTES + 1)
        if not data or len(data) > MAX_BYTES:
            raise HTTPException(413, "Source must be 1 byte to 4 MiB")
        digest = hashlib.sha256(data).hexdigest()
        scope_customer = customer if visibility == "customer" else None
        with connect(database_path) as database:
            existing = database.execute(
                "SELECT id FROM documents WHERE workspace=? AND source_hash=? AND json_extract(result,'$.provenance.conversion_path[0]')=? AND visibility=? AND customer IS ? AND json_extract(result,'$.provenance.config_revision')=? AND COALESCE(json_extract(result,'$.provenance.sales_import'),0)=?",
                (
                    user["workspace"],
                    digest,
                    name.rsplit(".", 1)[-1].lower(),
                    visibility,
                    scope_customer,
                    config.revision,
                    int(dataset),
                ),
            ).fetchone()
            if existing:
                return {"id": existing["id"], "duplicate": True}
            if (
                database.execute(
                    "SELECT COUNT(*) FROM documents WHERE workspace=?", (user["workspace"],)
                ).fetchone()[0]
                >= 200
            ):
                raise HTTPException(409, "Workspace document limit reached")
        result = convert_payload(name, data, config)
        identifier = str(uuid.uuid4())
        result["provenance"]["sales_import"] = bool(dataset)
        with connect(database_path) as database:
            # Reserve the write lock and recheck after conversion to prevent racing duplicate imports.
            database.execute("BEGIN IMMEDIATE")
            ensure_revision(database, user["workspace"], config)
            existing = database.execute(
                "SELECT id FROM documents WHERE workspace=? AND source_hash=? AND json_extract(result,'$.provenance.conversion_path[0]')=? AND visibility=? AND customer IS ? AND json_extract(result,'$.provenance.config_revision')=? AND COALESCE(json_extract(result,'$.provenance.sales_import'),0)=?",
                (
                    user["workspace"],
                    digest,
                    name.rsplit(".", 1)[-1].lower(),
                    visibility,
                    scope_customer,
                    config.revision,
                    int(dataset),
                ),
            ).fetchone()
            if existing:
                return {"id": existing["id"], "duplicate": True}
            if (
                database.execute(
                    "SELECT COUNT(*) FROM documents WHERE workspace=?", (user["workspace"],)
                ).fetchone()[0]
                >= 200
            ):
                raise HTTPException(409, "Workspace document limit reached")
            if dataset:
                if database.execute(
                    "SELECT 1 FROM sales_imports WHERE workspace=? AND source_hash=?",
                    (user["workspace"], digest),
                ).fetchone():
                    raise HTTPException(
                        409,
                        "Sales source already applied; changing visibility or configuration cannot duplicate sales",
                    )
                tables = [
                    block
                    for block in result.get("source_blocks", result["blocks"])
                    if block["kind"] == "table"
                ]
                if len(tables) != 1 or len(tables[0]["rows"]) < 2:
                    raise HTTPException(
                        422, "Sales import requires one table with header and data rows"
                    )
                rows = tables[0]["rows"]
                headers = rows[0]
                if any(alias not in headers for alias in config.data_columns.values()):
                    raise HTTPException(422, "Sales headers do not match configured column aliases")
                mapped = []
                for row in rows[1:]:
                    if len(row) != len(headers):
                        raise HTTPException(422, "Sales row width mismatch")
                    record = {
                        key: row[headers.index(alias)] for key, alias in config.data_columns.items()
                    }
                    if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", record["month"]) or any(
                        not re.fullmatch(r"\d{1,10}", record[key])
                        for key in ["quantity", "revenue_cents"]
                    ):
                        raise HTTPException(
                            422, "Invalid month or nonnegative integer sales values"
                        )
                    product = database.execute(
                        "SELECT customer FROM products WHERE workspace=? AND id=?",
                        (user["workspace"], record["product"]),
                    ).fetchone()
                    if not product or product["customer"] != record["customer"]:
                        raise HTTPException(422, "Unknown product/customer mapping")
                    mapped.append(
                        (
                            user["workspace"],
                            record["product"],
                            record["customer"],
                            record["month"],
                            int(record["quantity"]),
                            int(record["revenue_cents"]),
                        )
                    )
                database.executemany(
                    "INSERT INTO sales(workspace,product,customer,month,quantity,revenue_cents) VALUES (?,?,?,?,?,?)",
                    mapped,
                )
                database.execute(
                    "INSERT INTO sales_imports VALUES (?,?)", (user["workspace"], digest)
                )
            database.execute(
                "INSERT INTO documents(id,workspace,title,visibility,customer,category,result,source,source_hash) VALUES (?,?,?,?,?,?,?,?,?)",
                (
                    identifier,
                    user["workspace"],
                    name,
                    visibility,
                    scope_customer,
                    category,
                    json.dumps(result),
                    data,
                    digest,
                ),
            )
            audit(database, user, "import-sales" if dataset else "import-document", identifier)
        return {"id": identifier, "duplicate": False, "warnings": result["warnings"]}

    @app.post("/api/merge")
    def merge(body: MergeRequest, request: Request):
        """Combine authorized sources in caller order; restrictive scope prevents declassification."""
        user = authorize(request, {"employee", "admin"}, mutate=True)
        if len(set(body.ids)) != len(body.ids):
            raise HTTPException(422, "Duplicate source identifiers")
        sources = [accessible(request, identifier)[0] for identifier in body.ids]
        config = configuration(user["workspace"])
        blocks, warnings = [], []
        for source_row in sources:
            result = json.loads(source_row["result"])
            blocks.append({"kind": "heading", "text": source_row["title"]})
            blocks.extend(result.get("source_blocks", result["blocks"]))
            if "source_blocks" not in result:
                warnings.append(
                    "Legacy source uses previously normalized values; reimport originals for full precision."
                )
            warnings.extend(result["warnings"])
        provenance = {
            "schema_version": "1.0",
            "source_ids": body.ids,
            "config_revision": config.revision,
            "conversion_path": ["html", "combined-html"],
        }
        from .conversion import assemble

        try:
            result = assemble(body.title, blocks, provenance, config, warnings)
        except ValueError as error:
            raise HTTPException(422, str(error)) from error
        result["review_status"] = "needs-review"
        identifier = str(uuid.uuid4())
        with connect(database_path) as database:
            database.execute("BEGIN IMMEDIATE")
            ensure_revision(database, user["workspace"], config)
            if (
                database.execute(
                    "SELECT COUNT(*) FROM documents WHERE workspace=?", (user["workspace"],)
                ).fetchone()[0]
                >= 200
            ):
                raise HTTPException(409, "Workspace document limit reached")
            database.execute(
                "INSERT INTO documents(id,workspace,title,visibility,category,result) VALUES (?,?,?,'internal','Compilation',?)",
                (identifier, user["workspace"], body.title, json.dumps(result)),
            )
            audit(database, user, "merge", identifier)
        return {"id": identifier}

    @app.get("/api/config")
    def get_config(request: Request):
        """Admin-only configuration, revision and provider type; never return API keys."""
        user = authorize(request, {"admin"})
        return {
            "config": configuration(user["workspace"]).model_dump(),
            "ai_adapter": type(app.state.ai_adapter).__name__,
            "units": UNITS,
        }

    @app.put("/api/config")
    def save_config(body: WorkspaceConfig, request: Request):
        """Optimistic config update prevents lost edits; historical conversions remain immutable."""
        user = authorize(request, {"admin"}, mutate=True)
        if body.profile != user["workspace"]:
            raise HTTPException(422, "Profile must match workspace")
        with connect(database_path) as database:
            database.execute("BEGIN IMMEDIATE")
            previous = WorkspaceConfig.model_validate_json(
                database.execute(
                    "SELECT config FROM workspaces WHERE id=?", (user["workspace"],)
                ).fetchone()[0]
            )
            if body.revision != previous.revision:
                raise HTTPException(409, "Configuration changed; reload before saving")
            if (
                database.execute(
                    "SELECT COUNT(*) FROM config_history WHERE workspace=?", (user["workspace"],)
                ).fetchone()[0]
                >= 250
            ):
                raise HTTPException(
                    409,
                    "Standard history limit reached; preserve a backup and review a controlled history migration",
                )
            used = {
                row[0]
                for row in database.execute(
                    "SELECT customer FROM users WHERE workspace=? AND customer IS NOT NULL UNION SELECT customer FROM products WHERE workspace=? UNION SELECT customer FROM documents WHERE workspace=? AND customer IS NOT NULL",
                    [user["workspace"]] * 3,
                )
            }
            if not used.issubset(body.customers):
                raise HTTPException(
                    409,
                    "Cannot remove customer IDs still referenced by accounts, products or documents",
                )
            body.revision += 1
            database.execute(
                "UPDATE workspaces SET config=? WHERE id=?",
                (body.model_dump_json(), user["workspace"]),
            )
            audit(database, user, "configure", f"revision {body.revision}")
            database.execute(
                "INSERT INTO config_history(workspace,revision,config,actor) VALUES (?,?,?,?)",
                (user["workspace"], body.revision, body.model_dump_json(), user["username"]),
            )
        return body.model_dump()

    @app.post("/api/standards/preview")
    def preview_standard(body: StandardPreview, request: Request):
        """Validate and render a local CSV draft only for the authenticated standards authority."""
        user = authorize(request, {"admin"}, mutate=True)
        if body.config.profile != user["workspace"]:
            raise HTTPException(422, "Profile must match workspace")
        try:
            return ingest("standard-preview.csv", body.sample.encode(), body.config)
        except ValueError as error:
            raise HTTPException(422, str(error)) from error

    @app.post("/api/standards/preview-file")
    def preview_file(
        request: Request, file: UploadFile = File(), config: str = Form(max_length=64000)
    ):
        """Preview a supported real file with an authorized draft; never insert it or call AI."""
        user = authorize(request, {"admin"}, mutate=True)
        try:
            draft = WorkspaceConfig.model_validate_json(config)
        except ValueError as error:
            raise HTTPException(422, "Invalid draft standard") from error
        if draft.profile != user["workspace"]:
            raise HTTPException(422, "Profile must match workspace")
        return convert_payload(file.filename or "", file.file.read(MAX_BYTES + 1), draft)

    @app.get("/api/standards/history")
    def standard_history(request: Request):
        """Return only this authorized workspace's immutable configuration revisions."""
        user = authorize(request, {"admin"})
        with connect(database_path) as database:
            return [
                {
                    "revision": row["revision"],
                    "actor": row["actor"],
                    "created": row["created"],
                    "config": WorkspaceConfig.model_validate_json(row["config"]).model_dump(),
                }
                for row in database.execute(
                    "SELECT * FROM config_history WHERE workspace=? ORDER BY revision DESC LIMIT 250",
                    (user["workspace"],),
                )
            ]

    @app.post("/api/standards/restore")
    def restore_standard(body: StandardRestore, request: Request):
        """Publish a historical configuration as a new revision; never rewrite history."""
        user = authorize(request, {"admin"}, mutate=True)
        with connect(database_path) as database:
            row = database.execute(
                "SELECT config FROM config_history WHERE workspace=? AND revision=?",
                (user["workspace"], body.revision),
            ).fetchone()
        if not row:
            raise HTTPException(404, "Standard revision not found")
        restored = WorkspaceConfig.model_validate_json(row[0])
        restored.revision = body.expected_revision
        return save_config(restored, request)

    @app.post("/api/documents/{identifier}/standardize")
    def standardize_document(request: Request, identifier: str):
        """Make an explicitly requested current-standard copy; never replay sales or change access."""
        import io

        from .conversion import assemble

        user = authorize(request, {"employee", "admin"}, mutate=True)
        row, _ = accessible(request, identifier)
        old = json.loads(row["result"])
        config = configuration(user["workspace"])
        if row["source"] is not None:
            copied = upload(
                request,
                UploadFile(
                    filename=old["provenance"]["source_name"], file=io.BytesIO(row["source"])
                ),
                row["visibility"],
                row["customer"] or next(iter(config.customers)),
                row["category"],
                False,
            )
            if not copied["duplicate"]:
                with connect(database_path) as database:
                    database.execute(
                        "UPDATE documents SET product=? WHERE id=? AND workspace=?",
                        (row["product"], copied["id"], user["workspace"]),
                    )
                    audit(database, user, "standardize", identifier + " -> " + copied["id"])
            return copied
        if (
            old.get("standard", {}).get("sha256") == identity(config)["sha256"]
            and old.get("provenance", {}).get("config_revision") == config.revision
        ):
            return {"id": identifier, "duplicate": True}
        warnings = list(old["warnings"])
        if "source_blocks" not in old:
            warnings.append(
                "Legacy compilation values may already be rounded; reimport originals for full precision."
            )
        try:
            result = assemble(
                row["title"],
                old.get("source_blocks", old["blocks"]),
                {"source_ids": [identifier], "conversion_path": ["html", "standardized-html"]},
                config,
                warnings,
            )
        except ValueError as error:
            raise HTTPException(422, str(error)) from error
        new_id = str(uuid.uuid4())
        with connect(database_path) as database:
            database.execute("BEGIN IMMEDIATE")
            ensure_revision(database, user["workspace"], config)
            if (
                database.execute(
                    "SELECT COUNT(*) FROM documents WHERE workspace=?", (user["workspace"],)
                ).fetchone()[0]
                >= 200
            ):
                raise HTTPException(409, "Workspace document limit reached")
            database.execute(
                "INSERT INTO documents(id,workspace,title,visibility,customer,category,result) VALUES (?,?,?,?,?,?,?)",
                (
                    new_id,
                    user["workspace"],
                    row["title"],
                    row["visibility"],
                    row["customer"],
                    row["category"],
                    json.dumps(result),
                ),
            )
            audit(database, user, "standardize", new_id)
        return {"id": new_id, "duplicate": False}

    @app.get("/api/report")
    def sales_report(request: Request):
        """Customer-only sales subset or full employee/admin business reporting."""
        user = authorize(request)
        with connect(database_path) as database:
            config = configuration(user["workspace"])
            return report(database, user, config.forecasting) | {
                "standard": {
                    "name": config.output_standard.name,
                    "revision": config.revision,
                    "default_export": config.output_standard.default_export,
                    "enforce_export": config.output_standard.enforce_export,
                }
            }

    @app.get("/api/report/export/{format_name}")
    def export_report(request: Request, format_name: str):
        """Apply the active presentation/delivery standard to the caller's scoped sales report."""
        user = authorize(request)
        config = configuration(user["workspace"])
        if format_name not in FORMATS:
            raise HTTPException(400, "Unsupported export format")
        with connect(database_path) as database:
            data = report(database, user, config.forecasting)
        rows = [["Month", "Quantity", "Revenue (USD cents)"]] + [
            [str(row[key]) for key in ["month", "quantity", "revenue_cents"]]
            for row in data["series"]
        ]
        blocks = [{"kind": "table", "rows": rows}, {"kind": "paragraph", "text": data["method"]}]
        provenance = {
            "config_revision": config.revision,
            "standard_sha256": identity(config)["sha256"],
            "record_type": "scoped-sales-report",
            "conversion_path": ["database", "html"],
            "currency": "USD",
        }
        result = {
            "html": render_document(
                "Business performance report", blocks, [], provenance, config, []
            ),
            "blocks": blocks,
            "provenance": provenance,
            "standard": identity(config),
        }
        try:
            payload = export_document(result, format_name)
        except ValueError as error:
            raise HTTPException(422, str(error)) from error
        return Response(
            payload,
            media_type=FORMATS[format_name],
            headers={
                "Content-Disposition": f'attachment; filename="business-report.{format_name}"'
            },
        )

    @app.post("/api/units")
    def measurement(body: MeasurementRequest):
        """Public exact conversion utility with dimension and physical-range validation."""
        try:
            return {"value": convert(body.value, body.source, body.target), "unit": body.target}
        except ValueError as error:
            raise HTTPException(422, str(error)) from error

    @app.get("/api/audit")
    def audit_log(request: Request):
        """Admin-only bounded audit trail for the active organization."""
        user = authorize(request, {"admin"})
        with connect(database_path) as database:
            return [
                dict(row)
                for row in database.execute(
                    "SELECT actor,event,detail,created FROM audit WHERE workspace=? ORDER BY id DESC LIMIT 50",
                    (user["workspace"],),
                )
            ]

    def context_for(user: dict) -> list[dict]:
        """Apply ACL before any model receives bounded, machine-readable source chunks."""
        with connect(database_path) as database:
            rows = documents(database, user, user["workspace"])
        context = []
        budget = 20_000
        for row in rows:
            text = json.loads(row["result"])["text"][: min(2000, budget)]
            if not text:
                break
            context.append(
                {
                    "id": row["id"],
                    "title": row["title"],
                    "text": text,
                    "workspace": user["workspace"],
                    "visibility": row["visibility"],
                }
            )
            budget -= len(text)
        return context

    @app.post("/api/ask")
    def ask(body: Question, request: Request):
        """Optional read-only AI question with authorized sources and validated citations."""
        user = authorize(request, mutate=True)
        if not configuration(user["workspace"]).ai_enabled:
            raise HTTPException(409, "AI disabled; an administrator must explicitly enable it")
        context = context_for(user)
        try:
            return validate_answer(app.state.ai_adapter.answer(body.question, context), context)
        except Exception as error:
            raise HTTPException(502, "AI adapter failed safely; no changes were made") from error

    @app.post("/api/documents/{identifier}/vision/{index}")
    def vision(request: Request, identifier: str, index: int):
        """Explicit opt-in vision request, never automatic or silently accepted as extracted fact."""
        user = authorize(request, {"employee", "admin"}, mutate=True)
        row, _ = accessible(request, identifier)
        if not configuration(user["workspace"]).ai_enabled:
            raise HTTPException(409, "AI disabled")
        blocks = json.loads(row["result"])["blocks"]
        if index < 0 or index >= len(blocks) or blocks[index]["kind"] != "figure":
            raise HTTPException(422, "Select an existing figure")
        context = [{"id": row["id"], "title": row["title"], "text": blocks[index]["text"]}]
        try:
            return validate_answer(
                app.state.ai_adapter.answer(
                    "Describe the figure, axes, table or equation. Clearly mark uncertainty. Do not invent precise values.",
                    context,
                    blocks[index]["image"],
                ),
                context,
            )
        except Exception as error:
            raise HTTPException(502, "Vision adapter failed safely") from error

    if (ROOT / "dist").exists():
        app.mount("/", StaticFiles(directory=ROOT / "dist", html=True), name="website")
    return app


# The legacy demo is opt-in; importing the private service never opens old runtime data.
app = create_app() if os.environ.get("KB_LEGACY_MODE") == "1" else FastAPI(docs_url=None)
