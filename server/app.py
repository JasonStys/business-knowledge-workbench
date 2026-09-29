# @index-begin
# @symbol variable/parameter: ROOT L168
# @symbol variable/parameter: CONVERSION_SLOTS L169
# @symbol function/class: BodyLimit L172
# @symbol function/class: __init__ L175
# @symbol variable/parameter: self L175
# @symbol function/class: __call__ L179
# @symbol variable/parameter: receive L179
# @symbol variable/parameter: scope L179
# @symbol variable/parameter: send L179
# @symbol variable/parameter: chunks L183
# @symbol variable/parameter: total L184
# @symbol variable/parameter: message L186
# @symbol function/class: replay L198
# @symbol function/class: create_app L205
# @symbol variable/parameter: demo L205
# @symbol variable/parameter: path L205
# @symbol variable/parameter: database_path L207
# @symbol variable/parameter: secure L209
# @symbol variable/parameter: ai_adapter L211
# @symbol variable/parameter: login_attempts L212
# @symbol variable/parameter: attempts_lock L213
# @symbol variable/parameter: application L216
# @symbol function/class: lifespan L216
# @symbol variable/parameter: call_next L224
# @symbol variable/parameter: request L224
# @symbol function/class: security_headers L224
# @symbol variable/parameter: origin L226
# @symbol variable/parameter: allowed L227
# @symbol variable/parameter: response L234
# @symbol function/class: current L249
# @symbol variable/parameter: required L249
# @symbol variable/parameter: token L251
# @symbol variable/parameter: database L252
# @symbol variable/parameter: user L257
# @symbol function/class: authorize L262
# @symbol variable/parameter: mutate L262
# @symbol variable/parameter: roles L262
# @symbol function/class: configuration L273
# @symbol variable/parameter: workspace L273
# @symbol function/class: accessible L283
# @symbol variable/parameter: identifier L283
# @symbol variable/parameter: predicate L289
# @symbol variable/parameter: values L289
# @symbol function/class: health L299
# @symbol function/class: bootstrap L306
# @symbol variable/parameter: configs L309
# @symbol function/class: staff_options L332
# @symbol function/class: add_product L338
# @symbol variable/parameter: body L338
# @symbol variable/parameter: config L341
# @symbol variable/parameter: text L344
# @symbol function/class: login L384
# @symbol variable/parameter: address L386
# @symbol variable/parameter: now L387
# @symbol variable/parameter: recent L391
# @symbol variable/parameter: stamp L391
# @symbol variable/parameter: encoded L401
# @symbol variable/parameter: valid L402
# @symbol variable/parameter: csrf L405
# @symbol function/class: session L425
# @symbol variable/parameter: key L429
# @symbol function/class: logout L433
# @symbol function/class: products L446
# @symbol variable/parameter: q L447
# @symbol variable/parameter: rows L458
# @symbol function/class: list_documents L471
# @symbol variable/parameter: category L475
# @symbol variable/parameter: sort L476
# @symbol function/class: document L490
# @symbol variable/parameter: _ L492
# @symbol function/class: export L496
# @symbol variable/parameter: format_name L496
# @symbol variable/parameter: payload L501
# @symbol function/class: source L516
# @symbol variable/parameter: suffix L521
# @symbol function/class: upload L529
# @symbol variable/parameter: file L531
# @symbol variable/parameter: visibility L532
# @symbol variable/parameter: customer L533
# @symbol variable/parameter: dataset L535
# @symbol variable/parameter: name L546
# @symbol variable/parameter: data L552
# @symbol variable/parameter: digest L555
# @symbol variable/parameter: scope_customer L556
# @symbol variable/parameter: existing L558
# @symbol variable/parameter: worker_env L581
# @symbol variable/parameter: value L583
# @symbol variable/parameter: converted L586
# @symbol variable/parameter: block L632
# @symbol variable/parameter: tables L632
# @symbol variable/parameter: headers L638
# @symbol variable/parameter: alias L639
# @symbol variable/parameter: mapped L641
# @symbol variable/parameter: record L645
# @symbol variable/parameter: product L655
# @symbol function/class: merge L696
# @symbol variable/parameter: sources L701
# @symbol variable/parameter: measurements L703
# @symbol variable/parameter: warnings L703
# @symbol variable/parameter: source_row L704
# @symbol variable/parameter: provenance L710
# @symbol variable/parameter: html L716
# @symbol variable/parameter: result L721
# @symbol function/class: get_config L749
# @symbol function/class: save_config L759
# @symbol variable/parameter: previous L765
# @symbol variable/parameter: used L772
# @symbol function/class: sales_report L793
# @symbol function/class: measurement L800
# @symbol function/class: audit_log L808
# @symbol function/class: context_for L820
# @symbol variable/parameter: context L824
# @symbol variable/parameter: budget L825
# @symbol variable/parameter: row L826
# @symbol function/class: ask L843
# @symbol variable/parameter: index L855
# @symbol function/class: vision L855
# @symbol variable/parameter: blocks L861
# @symbol variable/parameter: app L882
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
from .models import (
    Login,
    MeasurementRequest,
    MergeRequest,
    ProductRequest,
    Question,
    WorkspaceConfig,
)
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


def create_app(path: Path | None = None, demo: bool | None = None) -> FastAPI:
    """Application factory supports isolated test databases and explicit demo enrollment."""
    database_path = path or Path(os.environ.get("KB_DB", ROOT / "data/workbench.sqlite"))
    demo = os.environ.get("KB_DEMO", "0") == "1" if demo is None else demo
    secure = os.environ.get("KB_SECURE_COOKIE", "0" if demo else "1") == "1"
    initialize(database_path, demo)
    ai_adapter = adapter()
    login_attempts: dict[str, list[float]] = {}
    attempts_lock = threading.Lock()

    @asynccontextmanager
    async def lifespan(application):
        """Keep application lifecycle explicit for hosting and browser tests."""
        yield

    app = FastAPI(title="Business Knowledge Workbench", version="1.0.0", lifespan=lifespan)
    app.add_middleware(BodyLimit)

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        """Enforce same-origin writes and prevent private response caching or active embedding."""
        origin = request.headers.get("origin")
        allowed = os.environ.get("KB_ORIGIN", "http://127.0.0.1:8000")
        if (
            request.method in {"POST", "PUT", "PATCH", "DELETE"}
            and origin
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

    @app.get("/api/documents/{identifier}")
    def document(request: Request, identifier: str):
        """Return authorized semantic content and provenance for human or machine consumption."""
        row, _ = accessible(request, identifier)
        return json.loads(row["result"])

    @app.get("/api/documents/{identifier}/export/{format_name}")
    def export(request: Request, identifier: str, format_name: str):
        """Download a conversion generated from persisted canonical HTML."""
        if format_name not in FORMATS:
            raise HTTPException(400, "Unsupported export format")
        row, _ = accessible(request, identifier)
        payload = export_document(json.loads(row["result"]), format_name)
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
                "SELECT id FROM documents WHERE workspace=? AND source_hash=? AND visibility=? AND customer IS ? AND json_extract(result,'$.provenance.config_revision')=? AND COALESCE(json_extract(result,'$.provenance.sales_import'),0)=?",
                (
                    user["workspace"],
                    digest,
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
        if not CONVERSION_SLOTS.acquire(blocking=False):
            raise HTTPException(429, "Conversion workers busy; retry later")
        try:
            worker_env = {
                key: value
                for key, value in os.environ.items()
                if key in {"PATH", "SystemRoot", "SYSTEMROOT", "TEMP", "TMP", "LANG"}
            }
            converted = subprocess.run(
                [sys.executable, "-m", "server.worker", name, config.model_dump_json()],
                input=data,
                capture_output=True,
                timeout=25,
                cwd=ROOT,
                env=worker_env,
                check=False,
            )
            payload = json.loads(converted.stdout)
            if converted.returncode or "result" not in payload:
                raise ValueError("Source rejected")
            result = payload["result"]
        except (ValueError, subprocess.TimeoutExpired) as error:
            raise HTTPException(
                422, "Conversion rejected: corrupt, unsafe, unsupported or over-budget file"
            ) from error
        finally:
            CONVERSION_SLOTS.release()
        identifier = str(uuid.uuid4())
        result["provenance"]["sales_import"] = bool(dataset)
        with connect(database_path) as database:
            # Reserve the write lock and recheck after conversion to prevent racing duplicate imports.
            database.execute("BEGIN IMMEDIATE")
            existing = database.execute(
                "SELECT id FROM documents WHERE workspace=? AND source_hash=? AND visibility=? AND customer IS ? AND json_extract(result,'$.provenance.config_revision')=? AND COALESCE(json_extract(result,'$.provenance.sales_import'),0)=?",
                (
                    user["workspace"],
                    digest,
                    visibility,
                    scope_customer,
                    config.revision,
                    int(dataset),
                ),
            ).fetchone()
            if existing:
                return {"id": existing["id"], "duplicate": True}
            if dataset:
                if database.execute(
                    "SELECT 1 FROM sales_imports WHERE workspace=? AND source_hash=?",
                    (user["workspace"], digest),
                ).fetchone():
                    raise HTTPException(
                        409,
                        "Sales source already applied; changing visibility or configuration cannot duplicate sales",
                    )
                tables = [block for block in result["blocks"] if block["kind"] == "table"]
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
        blocks, measurements, warnings = [], [], []
        for source_row in sources:
            result = json.loads(source_row["result"])
            blocks.append({"kind": "heading", "text": source_row["title"]})
            blocks.extend(result["blocks"])
            measurements.extend(result["measurements"])
            warnings.extend(result["warnings"])
        provenance = {
            "schema_version": "1.0",
            "source_ids": body.ids,
            "config_revision": config.revision,
            "conversion_path": ["html", "combined-html"],
        }
        html = render_document(body.title, blocks, measurements, provenance, config, warnings)
        if len(html.encode()) > 8 * 1024 * 1024:
            raise HTTPException(422, "Compilation exceeds output budget")
        from bs4 import BeautifulSoup

        result = {
            "schema_version": "1.0",
            "title": body.title,
            "blocks": blocks,
            "measurements": measurements,
            "warnings": warnings,
            "provenance": provenance,
            "html": html,
            "text": BeautifulSoup(html, "html.parser").get_text(" ", strip=True),
            "review_status": "needs-review",
        }
        identifier = str(uuid.uuid4())
        with connect(database_path) as database:
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
            "ai_adapter": type(ai_adapter).__name__,
            "units": UNITS,
        }

    @app.put("/api/config")
    def save_config(body: WorkspaceConfig, request: Request):
        """Optimistic config update prevents lost edits; historical conversions remain immutable."""
        user = authorize(request, {"admin"}, mutate=True)
        if body.profile != user["workspace"]:
            raise HTTPException(422, "Profile must match workspace")
        with connect(database_path) as database:
            previous = WorkspaceConfig.model_validate_json(
                database.execute(
                    "SELECT config FROM workspaces WHERE id=?", (user["workspace"],)
                ).fetchone()[0]
            )
            if body.revision != previous.revision:
                raise HTTPException(409, "Configuration changed; reload before saving")
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
        return body.model_dump()

    @app.get("/api/report")
    def sales_report(request: Request):
        """Customer-only sales subset or full employee/admin business reporting."""
        user = authorize(request)
        with connect(database_path) as database:
            return report(database, user, configuration(user["workspace"]).forecasting)

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
            return validate_answer(ai_adapter.answer(body.question, context), context)
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
                ai_adapter.answer(
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


app = create_app()
