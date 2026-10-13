# @index-begin
# @symbol variable/parameter: PASSWORD L86
# @symbol variable/parameter: KEY L87
# @symbol variable/parameter: SALT L88
# @symbol variable/parameter: HEADERS L89
# @symbol function/class: client L93
# @symbol variable/parameter: tmp_path L93
# @symbol variable/parameter: app L95
# @symbol variable/parameter: session L96
# @symbol variable/parameter: alias L100
# @symbol variable/parameter: client L100
# @symbol function/class: register L100
# @symbol variable/parameter: response L102
# @symbol variable/parameter: key L107
# @symbol function/class: unlock L107
# @symbol function/class: test_registration_private_headers_and_zero_secret_echo L113
# @symbol variable/parameter: invalid L128
# @symbol variable/parameter: db L132
# @symbol variable/parameter: row L133
# @symbol variable/parameter: headers L147
# @symbol function/class: test_request_origin_host_mutation_rejected L147
# @symbol function/class: test_recovery_logout_expiry_delete L159
# @symbol variable/parameter: recovery L161
# @symbol variable/parameter: body L163
# @symbol variable/parameter: changed L164
# @symbol function/class: test_expiry_and_human_idle L188
# @symbol variable/parameter: manager L192
# @symbol variable/parameter: human L193
# @symbol variable/parameter: monkeypatch L203
# @symbol function/class: test_recovery_save_failure_preserves_code L203
# @symbol variable/parameter: original L210
# @symbol variable/parameter: args L212
# @symbol function/class: unavailable L212
# @symbol variable/parameter: name L228
# @symbol function/class: test_archive_paths L228
# @symbol function/class: test_archive_authentication_before_extract L234
# @symbol variable/parameter: root L236
# @symbol variable/parameter: path L239
# @symbol variable/parameter: damaged L242
# @symbol function/class: test_single_instance_and_launcher_not_browser L250
# @symbol variable/parameter: content L257
# @symbol function/class: imported L257
# @symbol function/class: test_document_encryption_export_reopen L266
# @symbol variable/parameter: identity L270
# @symbol variable/parameter: document L271
# @symbol variable/parameter: fmt L274
# @symbol function/class: test_accounts_and_session_specific_unlock L297
# @symbol variable/parameter: suffix L324
# @symbol function/class: test_private_rich_imports L341
# @symbol variable/parameter: payload L345
# @symbol variable/parameter: result L347
# @symbol function/class: test_role_previews_and_seed_own_only L351
# @symbol function/class: test_provider_privacy_consent_and_offline_ai L377
# @symbol variable/parameter: config L382
# @symbol variable/parameter: offline L385
# @symbol variable/parameter: settings L387
# @symbol variable/parameter: saved L392
# @symbol variable/parameter: context L404
# @symbol variable/parameter: image L404
# @symbol variable/parameter: question L404
# @symbol variable/parameter: self L404
# @symbol variable/parameter: owner L425
# @symbol function/class: test_model_endpoint_rejections L443
# @symbol variable/parameter: url L443
# @symbol function/class: test_soft_quota_preserves_recovery L451
# @symbol function/class: test_body_and_auth_limits L467
# @symbol variable/parameter: _ L477
# @index-end
"""Jason Stys: actual private-account, archive, provider, ownership and blocked-execution regression tests.

All credentials/source are explicitly fictional and every filesystem root is disposable.
"""

import base64
import time
from pathlib import Path

import pytest
from cryptography.exceptions import InvalidTag
from fastapi.testclient import TestClient

from server.private_api import create_private_app
from server.store import connect
from server.vault import decrypt_workspace, encrypt_workspace, safe_name

PASSWORD = "synthetic-test-login-password-2026"  # noqa: S105 - disposable fixture only.
KEY = base64.b64encode(b"k" * 32).decode()
SALT = base64.b64encode(b"s" * 16).decode()
HEADERS = {"X-KBW-Request": "v1", "Origin": "http://127.0.0.1:8090"}


@pytest.fixture
def client(tmp_path):
    """Start actual local authentication and document engine with a disposable protected root."""
    app = create_private_app(tmp_path / "accounts", 8090)
    with TestClient(app, base_url="http://127.0.0.1:8090", headers=HEADERS) as session:
        yield session


def register(client, alias="fictional_one"):
    """Register a fictional password and capture its one-use recovery code for tests only."""
    response = client.post("/private/register", json={"alias": alias, "password": PASSWORD})
    assert response.status_code == 200
    return response.json()["recovery"]


def unlock(client, key=KEY):
    """Prove a synthetic derived key through the real route."""
    response = client.post("/private/unlock", json={"key": key, "salt": SALT})
    assert response.status_code == 200, response.text


def test_registration_private_headers_and_zero_secret_echo(client):
    """No seeded login, browser bearer or returned credential; API and mutation boundaries fail closed."""
    assert client.get("/private/account").status_code == 401
    assert client.get("/api/documents").status_code == 404
    response = client.post(
        "/private/register", json={"alias": "fictional_one", "password": PASSWORD}
    )
    assert (
        "HttpOnly" in response.headers["set-cookie"]
        and "SameSite=strict" in response.headers["set-cookie"]
    )
    assert PASSWORD not in response.text
    assert response.headers["cache-control"] == "no-store"
    assert "script-src 'self'" in response.headers["content-security-policy"]
    assert "frame-ancestors 'none'" in response.headers["content-security-policy"]
    invalid = client.post(
        "/private/login", json={"alias": "bad <script>", "password": PASSWORD, "role": "admin"}
    )
    assert invalid.status_code == 422 and PASSWORD not in invalid.text
    with client.app.state.manager.accounts.connection() as db:
        row = db.execute("SELECT password,recovery FROM accounts").fetchone()
        assert row[0].startswith("scrypt-v1$") and PASSWORD not in row[0]
        assert row[1] != response.json()["recovery"]


@pytest.mark.parametrize(
    "headers",
    [
        {"Host": "evil.example"},
        {"Origin": "https://evil.example"},
        {"X-KBW-Request": "wrong"},
        {"Sec-Fetch-Site": "cross-site"},
    ],
)
def test_request_origin_host_mutation_rejected(client, headers):
    """Cross-site calls cannot register accounts or cause side effects."""
    assert (
        client.post(
            "/private/register",
            headers=headers,
            json={"alias": "fictional_one", "password": PASSWORD},
        ).status_code
        == 403
    )


def test_recovery_logout_expiry_delete(client):
    """One-use recovery revokes old sessions but preserves the independent vault; deletion needs current password."""
    recovery = register(client)
    unlock(client)
    body = {"alias": "fictional_one", "password": PASSWORD + "-new", "recovery": recovery}
    changed = client.post("/private/reset", json=body)
    assert changed.status_code == 200 and changed.json()["recovery"] != recovery
    assert client.get("/private/account").status_code == 401
    assert client.post("/private/reset", json=body).status_code == 401
    assert (
        client.post(
            "/private/login", json={"alias": "fictional_one", "password": PASSWORD + "-new"}
        ).status_code
        == 200
    )
    unlock(client)
    assert (
        client.post("/private/delete", json={"password": PASSWORD, "confirm": True}).status_code
        == 401
    )
    assert (
        client.post(
            "/private/delete", json={"password": PASSWORD + "-new", "confirm": True}
        ).status_code
        == 200
    )
    assert client.get("/private/account").status_code == 401


def test_expiry_and_human_idle(client):
    """Session expiry and human timeout are independent of metadata polling."""
    register(client)
    unlock(client)
    manager = client.app.state.manager
    human = manager.last_human
    client.get("/private/account")
    assert manager.last_human == human
    assert client.post("/private/activity", json={"idle_seconds": 1800}).status_code == 200
    assert manager.idle_seconds == 1800
    with manager.accounts.connection() as db:
        db.execute("UPDATE sessions SET expires=?", (int(time.time()) - 1,))
    assert client.get("/private/account").status_code == 401


def test_recovery_save_failure_preserves_code(client, monkeypatch):
    """Failed sealing cannot consume the recovery code or drop its unsaved working data."""
    import server.private_workspace as workspace

    recovery = register(client)
    unlock(client)
    (client.app.state.manager.active / "change.txt").write_text("Synthetic unsaved change")
    original = workspace.encrypt_workspace

    def unavailable(*args):
        """Fail only this disposable test's encrypted disk write."""
        raise OSError("Synthetic disk failure")

    monkeypatch.setattr(workspace, "encrypt_workspace", unavailable)
    body = {"alias": "fictional_one", "password": PASSWORD + "-new", "recovery": recovery}
    assert client.post("/private/reset", json=body).status_code == 400
    assert client.app.state.manager.key is not None
    assert client.app.state.manager.accounts.login("fictional_one", PASSWORD)
    monkeypatch.setattr(workspace, "encrypt_workspace", original)
    assert client.post("/private/reset", json=body).status_code == 200


@pytest.mark.parametrize(
    "name", ["../escape", "a\\b", "C:/file", "a//b", "CON.txt", "a./b", "a\x00b"]
)
def test_archive_paths(name):
    """Portable extraction never permits traversal/devices/ambiguous names."""
    with pytest.raises(ValueError):
        safe_name(name)


def test_archive_authentication_before_extract(tmp_path):
    """Tampered GCM tags expose no extracted plaintext; preexisting directories are never overwritten."""
    root = tmp_path / "source"
    root.mkdir()
    (root / "code.txt").write_text("synthetic sensitive marker")
    path = tmp_path / "source.kbwvault"
    encrypt_workspace(root, path, b"k" * 32)
    assert b"synthetic sensitive marker" not in path.read_bytes()
    damaged = bytearray(path.read_bytes())
    damaged[-1] ^= 1
    path.write_bytes(damaged)
    with pytest.raises(InvalidTag):
        decrypt_workspace(path, tmp_path / "bad", b"k" * 32)
    assert not (tmp_path / "bad").exists()


def test_single_instance_and_launcher_not_browser(client):
    """Only the process-local launcher can shut down, and a second instance cannot share active files."""
    assert client.post("/launcher/shutdown", json={}).status_code == 403
    with pytest.raises(ValueError, match="Another"):
        create_private_app(client.app.state.manager.root, 8091)


def imported(client, name="private.txt", content=b"Private evidence: Width 4.25 in"):
    """Real multipart import through the credential-stripped document worker."""
    response = client.post(
        "/private/api/import", files={"file": (name, content)}, data={"visibility": "internal"}
    )
    assert response.status_code == 200, response.text
    return response.json()["id"]


def test_document_encryption_export_reopen(client):
    """A genuine worker result, HTML-first exports and original evidence survive encrypted reopen."""
    register(client)
    unlock(client)
    identity = imported(client)
    document = client.get("/private/api/documents/" + identity).json()
    assert "107.95 mm" in document["html"]
    assert document["provenance"]["conversion_path"][-1] == "html"
    for fmt in ["html", "json", "md", "docx", "pdf"]:
        assert client.get(f"/private/api/documents/{identity}/export/{fmt}").status_code == 200
    assert (
        client.get(f"/private/api/documents/{identity}/source").content
        == b"Private evidence: Width 4.25 in"
    )
    manager, owner = client.app.state.manager, client.app.state.manager.owner
    assert client.post("/private/save", json={}).status_code == 200
    assert client.post("/private/lock", json={}).status_code == 200
    assert not manager.active.exists()
    assert b"Private evidence" not in manager.archive(owner).read_bytes()
    assert client.get("/private/api/documents").status_code == 423
    assert (
        client.post(
            "/private/unlock", json={"key": base64.b64encode(b"w" * 32).decode()}
        ).status_code
        == 400
    )
    unlock(client)
    assert client.get("/private/api/documents/" + identity).json() == document
    assert client.get("/private/backup").content.startswith(b"KBWV0001")


def test_accounts_and_session_specific_unlock(client):
    """A new same-account login needs key proof; unrelated accounts cannot guess source/download IDs."""
    register(client)
    unlock(client)
    identity = imported(client)
    original = dict(client.cookies)
    client.cookies.clear()
    assert (
        client.post(
            "/private/login", json={"alias": "fictional_one", "password": PASSWORD}
        ).status_code
        == 200
    )
    assert not client.get("/private/account").json()["unlocked"]
    assert client.get("/private/api/documents/" + identity).status_code == 423
    unlock(client)
    assert client.get("/private/api/documents/" + identity).status_code == 200
    client.cookies.clear()
    register(client, "fictional_two")
    assert client.post("/private/unlock", json={"key": KEY, "salt": SALT}).status_code == 400
    assert client.post("/private/logout", json={}).status_code == 200
    client.cookies.update(original)
    assert client.post("/private/lock", json={}).status_code == 200
    client.cookies.clear()
    client.post("/private/login", json={"alias": "fictional_two", "password": PASSWORD})
    unlock(client)
    assert client.get("/private/api/documents").json() == []
    for suffix in ["", "/source", "/export/json"]:
        assert client.get("/private/api/documents/" + identity + suffix).status_code == 404


@pytest.mark.parametrize(
    "name",
    [
        "commissioning-pack.docx",
        "controller-performance.pdf",
        "renewable-specifications.xlsx",
        "throughput.png",
        "laboratory-record.json",
        "installation-note.md",
        "service-record.xml",
        "mixed-measurements.csv",
    ],
)
def test_private_rich_imports(client, name):
    """Use real synthetic rich-format files, not parser mocks, through private conversion workers."""
    register(client)
    unlock(client)
    payload = (Path(__file__).resolve().parents[2] / "examples" / name).read_bytes()
    identity = imported(client, name, payload)
    result = client.get("/private/api/documents/" + identity).json()
    assert result["blocks"] and result["html"].startswith("<!doctype html>")


def test_role_previews_and_seed_own_only(client):
    """Synthetic examples are opt-in without demo passwords; lowered preview gates still apply."""
    register(client)
    unlock(client)
    assert client.get("/private/api/products").json() == []
    assert client.post("/private/seed", json={}).status_code == 200
    assert len(client.get("/private/api/products").json()) == 3
    assert len(client.get("/private/api/report").json()["series"]) == 12
    with connect(client.app.state.manager.active / "workbench.sqlite") as db:
        assert db.execute("SELECT count(*) FROM users").fetchone()[0] == 0
    headers = {"X-KBW-View": "customer"}
    assert client.get("/private/api/config", headers=headers).status_code == 403
    assert (
        client.get("/private/api/documents/industrial-PS-24-service", headers=headers).status_code
        == 404
    )
    assert (
        client.get(
            "/private/api/documents/industrial-MC-240-operations", headers={"X-KBW-View": "visitor"}
        ).status_code
        == 404
    )
    assert client.get("/private/api/products?workspace=another-owner").status_code == 422
    assert client.post("/private/api/login", json={}).status_code == 403


def test_provider_privacy_consent_and_offline_ai(client, monkeypatch):
    """Own key never returned; explicit revision consent precedes a mocked compatible-provider call."""
    register(client)
    unlock(client)
    identity = imported(client)
    config = client.get("/private/api/config").json()["config"]
    config["ai_enabled"] = True
    assert client.put("/private/api/config", json=config).status_code == 200
    offline = client.post("/private/api/ask", json={"question": "What is the width?"})
    assert offline.status_code == 200 and offline.json()["provider"] == "extractive"
    settings = {
        "endpoint": "https://api.openai.com/v1/chat/completions",
        "model": "synthetic-model",
        "key": "synthetic-provider-key-only",
    }
    saved = client.put("/private/providers", json=settings)
    assert (
        saved.status_code == 200 and settings["key"] not in saved.text and saved.json()["has_key"]
    )
    assert (
        client.post("/private/api/ask", json={"question": "What is the width?"}).status_code == 409
    )
    from server.ai import CompatibleAdapter

    monkeypatch.setattr(
        CompatibleAdapter,
        "answer",
        lambda self, question, context, image=None: {
            "answer": "Synthetic contract result",
            "citations": [identity],
            "provider": "compatible",
        },
    )
    response = client.post(
        "/private/api/ask",
        headers={"X-KBW-Provider-Revision": saved.json()["revision"]},
        json={"question": "What is the width?"},
    )
    assert response.status_code == 200 and response.json()["review_status"] == "unverified"
    changed = client.put("/private/providers", json=settings).json()
    assert changed["revision"] != saved.json()["revision"]
    assert (
        client.put(
            "/private/providers",
            json={"endpoint": "http://127.0.0.1:11434/v1/chat/completions", "retain_key": True},
        ).status_code
        == 400
    )
    owner = client.app.state.manager.owner
    assert client.post("/private/lock", json={}).status_code == 200
    assert settings["key"].encode() not in client.app.state.manager.archive(owner).read_bytes()
    unlock(client)
    assert client.get("/private/providers").json()["has_key"]


@pytest.mark.parametrize(
    "url",
    [
        "http://169.254.169.254/v1/chat/completions",
        "http://localhost:11434/v1/chat/completions",
        "https://evil.example/api",
        "file:///secret",
        "http://127.0.0.1:22/v1/chat/completions",
        "http://127.0.0.1:11434/v1/chat/completions?key=bad",
    ],
)
def test_model_endpoint_rejections(url):
    """Model URL selection cannot access metadata, arbitrary remote hosts or injected local schemes."""
    from server.private_api import Settings

    with pytest.raises(ValueError):
        Settings(endpoint=url)


def test_soft_quota_preserves_recovery(client, monkeypatch):
    """Stop mutations before archive reserves are exhausted, while keeping lock/reopen/export available."""
    import server.private_api as boundary

    register(client)
    unlock(client)
    identity = imported(client)
    monkeypatch.setattr(boundary, "HISTORY_STOP_BYTES", 1)
    assert (
        client.post("/private/api/import", files={"file": ("another.txt", b"x")}).status_code == 409
    )
    assert client.post("/private/lock", json={}).status_code == 200
    unlock(client)
    assert client.get("/private/api/documents/" + identity).status_code == 200


def test_body_and_auth_limits(client):
    """Bound actual streamed body bytes; durable auth throttles are separate from request limits."""
    assert (
        client.post(
            "/private/register",
            content=b"x" * (4 * 1024**2 + 64001),
            headers={"Content-Type": "application/json"},
        ).status_code
        == 413
    )
    for _ in range(10):
        assert (
            client.post(
                "/private/login", json={"alias": "fictional_missing", "password": PASSWORD}
            ).status_code
            == 401
        )
    assert (
        client.post(
            "/private/login", json={"alias": "fictional_missing", "password": PASSWORD}
        ).status_code
        == 429
    )
