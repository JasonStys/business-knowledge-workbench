# @index-begin
# @symbol variable/parameter: EXAMPLES L62
# @symbol function/class: client L66
# @symbol variable/parameter: tmp_path L66
# @symbol variable/parameter: client L72
# @symbol variable/parameter: role L72
# @symbol function/class: sign_in L72
# @symbol variable/parameter: workspace L72
# @symbol variable/parameter: response L74
# @symbol variable/parameter: fields L82
# @symbol variable/parameter: name L82
# @symbol function/class: upload L82
# @symbol function/class: test_public_boundary L89
# @symbol variable/parameter: docs L95
# @symbol variable/parameter: endpoint L99
# @symbol function/class: test_customer_isolation L107
# @symbol variable/parameter: row L113
# @symbol variable/parameter: north L120
# @symbol variable/parameter: south L124
# @symbol function/class: test_sessions_csrf_origin L129
# @symbol variable/parameter: csrf L146
# @symbol function/class: test_rate_limit L159
# @symbol variable/parameter: _ L161
# @symbol function/class: test_import_preview_export_duplicate L177
# @symbol variable/parameter: identifier L182
# @symbol variable/parameter: result L183
# @symbol variable/parameter: format_name L187
# @symbol function/class: test_rich_worker_files L210
# @symbol function/class: test_import_rejections L218
# @symbol function/class: test_sales_mapping_atomicity L232
# @symbol variable/parameter: before L235
# @symbol variable/parameter: after L238
# @symbol variable/parameter: body L244
# @symbol function/class: test_merge_and_config L259
# @symbol variable/parameter: ids L262
# @symbol variable/parameter: document L266
# @symbol variable/parameter: current L279
# @symbol variable/parameter: monkeypatch L300
# @symbol function/class: test_ai_acl_and_disable L300
# @symbol variable/parameter: config L305
# @symbol variable/parameter: image L307
# @symbol function/class: test_units_api L320
# @symbol function/class: test_database_lifecycle L334
# @symbol variable/parameter: path L336
# @symbol variable/parameter: database L338
# @symbol function/class: test_timeout_and_worker_busy L352
# @symbol variable/parameter: args L358
# @symbol variable/parameter: kwargs L358
# @symbol function/class: timeout L358
# @index-end
"""End-to-end API security, persistence and workflow regressions. Index: docs/code-index.md."""

import subprocess
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from server.app import create_app
from server.store import acl, connect, initialize

EXAMPLES = Path(__file__).resolve().parents[2] / "examples"


@pytest.fixture
def client(tmp_path):
    """Give each test a fresh database with the same synthetic demo scenarios."""
    with TestClient(create_app(tmp_path / "workbench.sqlite", True)) as client:
        yield client


def sign_in(client, role="admin", workspace="industrial"):
    """Authenticate through the real login endpoint and attach the returned CSRF token."""
    response = client.post(
        "/api/login", json={"workspace": workspace, "username": role, "password": "workbench-demo"}
    )
    assert response.status_code == 200
    client.headers["x-csrf-token"] = response.json()["csrf"]
    return response.json()


def upload(client, name="mixed-measurements.csv", **fields):
    """Upload one real source through multipart parsing and the isolated worker."""
    return client.post(
        "/api/import", files={"file": (name, (EXAMPLES / name).read_bytes())}, data=fields
    )


def test_public_boundary(client):
    """Visitors see public catalog/docs, never reports, configuration or private originals."""
    assert client.get("/api/health").json()["status"] == "ok"
    assert len(client.get("/api/bootstrap").json()["workspaces"]) == 3
    assert len(client.get("/api/products").json()) == 3
    assert len(client.get("/api/products?q=io-16").json()) == 1
    docs = client.get("/api/documents").json()
    assert len(docs) == 3 and all(row["visibility"] == "public" for row in docs)
    assert client.get("/api/documents/industrial-MC-240-operations").status_code == 404
    assert client.get("/api/documents/industrial-MC-240-service/source").status_code == 404
    for endpoint in ["report", "config", "audit"]:
        assert client.get("/api/" + endpoint).status_code == 401
    assert client.get("/api/documents?sort=unsafe").status_code == 422
    assert client.get("/api/documents?q=%25").json() == []
    assert len(client.get("/api/documents?category=Overview&sort=category").json()) == 3
    assert client.get("/api/documents?sort=newest").status_code == 200


def test_customer_isolation(client):
    """North customers cannot retrieve south records through direct IDs, search or exports."""
    sign_in(client, "customer")
    assert len(client.get("/api/products").json()) == 2
    docs = client.get("/api/documents").json()
    assert len(docs) == 5
    assert all(row["visibility"] != "internal" for row in docs)
    assert client.get("/api/documents/industrial-PS-24-service").status_code == 404
    assert client.get("/api/documents/renewable-SE-410-service").status_code == 404
    assert client.get("/api/documents/industrial-PS-24-service/export/json").status_code == 404
    assert client.get("/api/documents/industrial-MC-240-service/source").status_code == 200
    assert client.get("/api/config").status_code == 403
    assert upload(client).status_code == 403
    north = client.get("/api/report").json()
    assert len(north["series"]) == 12 and len(north["forecast"]) == 3
    client.post("/api/logout")
    sign_in(client, "customer-south")
    south = client.get("/api/report").json()
    assert north["revenue_cents"] > south["revenue_cents"]
    assert len(client.get("/api/products").json()) == 1


def test_sessions_csrf_origin(client):
    """Opaque cookies are HttpOnly and strict; CSRF and hostile-origin mutations fail."""
    assert client.get("/api/session").json() is None
    assert (
        client.post(
            "/api/login", json={"workspace": "industrial", "username": "missing", "password": "bad"}
        ).status_code
        == 401
    )
    assert (
        client.post(
            "/api/login", json={"workspace": "industrial", "username": "admin", "password": "bad"}
        ).status_code
        == 401
    )
    sign_in(client)
    assert client.get("/api/session").json()["role"] == "admin"
    csrf = client.headers.pop("x-csrf-token")
    assert client.post("/api/logout").status_code == 403
    client.headers["x-csrf-token"] = csrf
    assert (
        client.post("/api/logout", headers={"Origin": "https://attacker.test"}).status_code == 403
    )
    response = client.post("/api/logout")
    assert response.status_code == 200
    assert client.get("/api/session").json() is None
    assert response.headers["cache-control"] == "no-store"
    assert "nosniff" in response.headers["x-content-type-options"]


def test_rate_limit(client):
    """Repeated failed authentication is bounded per source address."""
    for _ in range(10):
        assert (
            client.post(
                "/api/login",
                json={"workspace": "industrial", "username": "admin", "password": "wrong"},
            ).status_code
            == 401
        )
    assert (
        client.post(
            "/api/login", json={"workspace": "industrial", "username": "admin", "password": "wrong"}
        ).status_code
        == 429
    )


def test_import_preview_export_duplicate(client):
    """Real worker import, persistence, provenance, source retention and each export work together."""
    sign_in(client, "employee")
    response = upload(client, visibility="internal")
    assert response.status_code == 200, response.text
    identifier = response.json()["id"]
    result = client.get("/api/documents/" + identifier).json()
    assert result["measurements"][0]["value"] == "107.95"
    assert result["provenance"]["conversion_path"] == ["csv", "html"]
    assert upload(client, visibility="internal").json() == {"id": identifier, "duplicate": True}
    for format_name in ["html", "json", "md", "csv", "docx", "pdf"]:
        response = client.get(f"/api/documents/{identifier}/export/{format_name}")
        assert response.status_code == 200 and response.content
    assert (
        "sandbox"
        in client.get(f"/api/documents/{identifier}/export/html").headers["content-security-policy"]
    )
    assert client.get(f"/api/documents/{identifier}/export/exe").status_code == 400
    assert (
        client.get(f"/api/documents/{identifier}/source").content
        == (EXAMPLES / "mixed-measurements.csv").read_bytes()
    )


@pytest.mark.parametrize(
    "name",
    [
        "commissioning-pack.docx",
        "controller-performance.pdf",
        "renewable-specifications.xlsx",
        "throughput.png",
    ],
)
def test_rich_worker_files(client, name):
    """Rich-format adapters run successfully through the actual credential-free worker."""
    sign_in(client)
    response = upload(client, name, visibility="customer", customer="north")
    assert response.status_code == 200, response.text
    assert client.get("/api/documents/" + response.json()["id"]).json()["warnings"]


def test_import_rejections(client):
    """Unsafe names, unsupported payloads, bad scope and over-budget bodies fail safely."""
    sign_in(client)
    for name in ["../../escape.txt", "script.exe", "file:ads.txt"]:
        assert client.post("/api/import", files={"file": (name, b"test")}).status_code == 415
    assert client.post("/api/import", files={"file": ("bad.pdf", b"not a pdf")}).status_code == 422
    assert client.post("/api/import", files={"file": ("empty.txt", b"")}).status_code == 413
    assert (
        client.post("/api/import", files={"file": ("big.txt", b"x" * 4_300_000)}).status_code == 413
    )
    assert upload(client, visibility="secret").status_code == 422
    assert upload(client, customer="unknown").status_code == 422


def test_sales_mapping_atomicity(client):
    """Validated mapped sales rows update reports; invalid rows never partially commit."""
    sign_in(client)
    before = client.get("/api/report").json()["revenue_cents"]
    response = upload(client, "industrial-sales.csv", dataset="true")
    assert response.status_code == 200, response.text
    after = client.get("/api/report").json()["revenue_cents"]
    assert after - before == 4231300
    assert upload(client, "industrial-sales.csv", dataset="true").json()["duplicate"]
    assert client.get("/api/report").json()["revenue_cents"] == after
    assert upload(client, dataset="true").status_code == 422
    assert upload(client, "throughput.png", dataset="true").status_code == 422
    for body in [
        b"product,customer,month,quantity,revenue_cents\nMC-240,north,2026-99,1,100",
        b"product,customer,month,quantity,revenue_cents\nNOPE,north,2026-02,1,100",
        b"product,customer,month,quantity,revenue_cents\nMC-240,north,2026-02,-1,100",
        b"product,customer,month,quantity,revenue_cents\nMC-240,north,2026-02,1",
    ]:
        assert (
            client.post(
                "/api/import", files={"file": ("bad.csv", body)}, data={"dataset": "true"}
            ).status_code
            == 422
        )
    assert client.get("/api/report").json()["revenue_cents"] == after


def test_merge_and_config(client):
    """Ordered compilation never declassifies sources; config revisions use optimistic locking."""
    sign_in(client)
    ids = ["industrial-MC-240-overview", "industrial-IO-16-operations"]
    response = client.post("/api/merge", json={"ids": ids, "title": "Evidence pack"})
    assert response.status_code == 200
    identifier = response.json()["id"]
    document = client.get("/api/documents/" + identifier).json()
    assert document["provenance"]["source_ids"] == ids
    assert client.get("/api/documents/" + identifier + "/source").status_code == 404
    assert (
        client.post("/api/merge", json={"ids": [ids[0], ids[0]], "title": "Bad pack"}).status_code
        == 422
    )
    assert (
        client.post(
            "/api/merge", json={"ids": ["renewable-SE-410-overview"], "title": "Cross tenant"}
        ).status_code
        == 404
    )
    current = client.get("/api/config").json()["config"]
    assert (
        client.put(
            "/api/config",
            json={
                **current,
                "title": "Renamed workspace",
                "units": {"length": "cm"},
                "forecasting": False,
            },
        ).json()["revision"]
        == 2
    )
    assert client.put("/api/config", json=current).status_code == 409
    assert client.put("/api/config", json={**current, "profile": "renewable"}).status_code == 422
    assert client.get("/api/report").json()["forecast"] == []
    assert client.get("/api/audit").json()[0]["event"] == "configure"
    client.post("/api/logout")
    assert client.get("/api/documents/" + identifier).status_code == 404


def test_ai_acl_and_disable(client, monkeypatch):
    """AI is opt-in; north context excludes south/private/internal evidence."""
    assert client.post("/api/ask", json={"question": "controller"}).status_code == 401
    sign_in(client)
    assert client.post("/api/ask", json={"question": "controller"}).status_code == 409
    config = client.get("/api/config").json()["config"]
    client.put("/api/config", json={**config, "ai_enabled": True})
    image = upload(client, "throughput.png").json()["id"]
    assert client.post(f"/api/documents/{image}/vision/0").status_code == 200
    assert client.post(f"/api/documents/{image}/vision/99").status_code == 422
    client.post("/api/logout")
    sign_in(client, "customer")
    response = client.post("/api/ask", json={"question": "controller width"})
    assert response.status_code == 200
    for identifier in response.json()["citations"]:
        assert client.get("/api/documents/" + identifier).status_code == 200
        assert "operations" not in identifier and "PS-24-service" not in identifier
    assert client.post(f"/api/documents/{image}/vision/0").status_code == 403


def test_units_api(client):
    """Public utility reports finite normalized values and meaningful validation errors."""
    assert (
        client.post("/api/units", json={"value": "1", "source": "in", "target": "mm"}).json()[
            "value"
        ]
        == "25.4"
    )
    assert (
        client.post("/api/units", json={"value": "NaN", "source": "in", "target": "mm"}).status_code
        == 422
    )


def test_database_lifecycle(tmp_path):
    """No demo accounts/data are provisioned in normal mode; seeding is idempotent."""
    path = tmp_path / "data.sqlite"
    initialize(path, False)
    with connect(path) as database:
        assert database.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0
        assert database.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0
    initialize(path, True)
    initialize(path, True)
    with connect(path) as database:
        assert database.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 9
        database.execute("PRAGMA user_version=99")
    with pytest.raises(ValueError):
        initialize(path, True)
    with pytest.raises(PermissionError):
        acl({"workspace": "laboratory"}, "industrial")


def test_timeout_and_worker_busy(client, monkeypatch):
    """Worker timeout is recoverable and an occupied worker pool rejects additional work."""
    from server.app import CONVERSION_SLOTS

    sign_in(client)

    def timeout(*args, **kwargs):
        """Simulate a parser exceeding its deadline."""
        raise subprocess.TimeoutExpired("worker", 25)

    monkeypatch.setattr(subprocess, "run", timeout)
    assert upload(client).status_code == 422
    CONVERSION_SLOTS.acquire()
    CONVERSION_SLOTS.acquire()
    try:
        assert upload(client).status_code == 429
    finally:
        CONVERSION_SLOTS.release()
        CONVERSION_SLOTS.release()
