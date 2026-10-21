# @index-begin
# @symbol variable/parameter: changes L95
# @symbol function/class: settings L95
# @symbol function/class: columns L100
# @symbol variable/parameter: extension L126
# @symbol variable/parameter: payload L126
# @symbol function/class: test_schema_and_units_across_formats L126
# @symbol variable/parameter: config L128
# @symbol variable/parameter: result L129
# @symbol variable/parameter: warning L138
# @symbol function/class: test_reject_invalid_schema_data L155
# @symbol function/class: test_declared_source_units_and_matching_scope L161
# @symbol variable/parameter: fields L163
# @symbol variable/parameter: other L170
# @symbol function/class: test_schema_for_rich_tables L188
# @symbol variable/parameter: doc L192
# @symbol variable/parameter: table L193
# @symbol variable/parameter: document L196
# @symbol variable/parameter: workbook L198
# @symbol variable/parameter: sheet L201
# @symbol variable/parameter: html L203
# @symbol variable/parameter: data L204
# @symbol variable/parameter: name L204
# @symbol variable/parameter: block L210
# @symbol variable/parameter: tables L210
# @symbol function/class: test_html_text_stays_inert_during_schema_expansion L219
# @symbol function/class: test_unsupported_merged_html_tables_fail_closed L237
# @symbol variable/parameter: standard L259
# @symbol function/class: test_safe_template_validation L259
# @symbol function/class: test_render_and_exports_use_snapshot L265
# @symbol variable/parameter: docx L280
# @symbol variable/parameter: pdf L283
# @symbol function/class: test_reapply_from_extracted_evidence_and_budget L294
# @symbol variable/parameter: first L296
# @symbol variable/parameter: second L297
# @symbol function/class: client L311
# @symbol variable/parameter: tmp_path L311
# @symbol variable/parameter: session L313
# @symbol variable/parameter: client L317
# @symbol function/class: login L317
# @symbol variable/parameter: role L317
# @symbol variable/parameter: response L319
# @symbol function/class: test_authority_preview_history_restore L327
# @symbol variable/parameter: before L331
# @symbol variable/parameter: draft L332
# @symbol variable/parameter: preview L335
# @symbol variable/parameter: item L342
# @symbol variable/parameter: restored L343
# @symbol variable/parameter: body L360
# @symbol variable/parameter: method L360
# @symbol function/class: test_current_copy_and_mixed_revision_merge L369
# @symbol variable/parameter: original L376
# @symbol variable/parameter: count_before L383
# @symbol variable/parameter: copy_id L384
# @symbol variable/parameter: copied L386
# @symbol variable/parameter: combined L391
# @symbol variable/parameter: record L396
# @symbol function/class: test_legacy_config_migration_is_idempotent L406
# @symbol variable/parameter: path L408
# @symbol variable/parameter: old L410
# @symbol variable/parameter: db L413
# @symbol variable/parameter: rows L419
# @symbol function/class: test_simultaneous_publication_has_one_winner L429
# @symbol variable/parameter: pool L435
# @symbol variable/parameter: outcomes L436
# @symbol variable/parameter: _ L437
# @symbol variable/parameter: row L440
# @symbol function/class: test_sales_aliases_remain_input_contract L443
# @symbol function/class: test_identical_bytes_with_different_formats_are_not_wrongly_deduplicated L468
# @symbol variable/parameter: text L472
# @symbol variable/parameter: csv L473
# @index-end
"""Jason Stys: standards schema, layout, authority, immutable history and migration regressions.

Functions/variables and exact lines: docs/code-index.md. All data and accounts are fictional.
"""

import copy
import io
import json

import pytest
from docx import Document
from fastapi.testclient import TestClient
from pypdf import PdfReader

from server.app import create_app
from server.conversion import assemble, ingest
from server.exports import export_document
from server.models import WorkspaceConfig
from server.standards import identity
from server.store import connect, initialize


def settings(**changes):
    """Return an explicit measurement standard with stable keys independent of source labels."""
    return WorkspaceConfig(title="Fictional standards business", profile="industrial", **changes)


def columns():
    """Two fields allow inline mixed units, while an optional third field stays present and empty."""
    return [
        {"key": "item", "label": "Component", "aliases": ["part"], "required": True},
        {
            "key": "width",
            "label": "Width",
            "aliases": ["length"],
            "dimension": "length",
            "required": True,
        },
        {"key": "note", "label": "Note", "required": False},
    ]


@pytest.mark.parametrize(
    "extension,payload",
    [
        ("csv", b"length,part,extra\n4.25 in,Panel,retained\n8.2 cm,Bracket,also retained"),
        ("tsv", b"length\tpart\textra\n4.25 in\tPanel\tretained\n8.2 cm\tBracket\talso retained"),
        (
            "json",
            b'[{"length":"4.25 in","part":"Panel","extra":"retained"},{"length":"8.2 cm","part":"Bracket","extra":"also retained"}]',
        ),
    ],
)
def test_schema_and_units_across_formats(extension, payload):
    """Different files converge on the same canonical keys/order/units without losing extras."""
    config = settings(output_standard={"columns": columns()})
    result = ingest("sample." + extension, payload, config)
    assert result["blocks"][0]["rows"] == [
        ["item", "width", "note", "extra"],
        ["Panel", "107.95 mm", "", "retained"],
        ["Bracket", "82 mm", "", "also retained"],
    ]
    assert result["source_blocks"][0]["rows"][0] == ["length", "part", "extra"]
    assert result["standard"] == identity(config)
    assert "<th>Component</th>" in result["html"]
    assert any("retained" in warning for warning in result["warnings"])
    assert "Component,Width,Note,extra" in export_document(result, "csv").decode("utf-8-sig")
    assert json.loads(export_document(result, "json"))["blocks"] == result["blocks"]


@pytest.mark.parametrize(
    "payload",
    [
        b"part,length\nPanel,3 kg",
        b"part,length\nPanel,3",
        b"part,length\n,3 in",
        b"part,length\nPanel,NaN in",
        b"part,length\nPanel,3 in,extra",
        b"part,length,width\nPanel,3 in,4 in",
        b"part\nPanel",
    ],
)
def test_reject_invalid_schema_data(payload):
    """Missing, duplicate, ragged, ambiguous, dimensionally wrong and nonfinite fields fail closed."""
    with pytest.raises(ValueError):
        ingest("sample.csv", payload, settings(output_standard={"columns": columns()}))


def test_declared_source_units_and_matching_scope():
    """Bare numbers need an explicit source-unit declaration; unrelated tables are flagged or rejected."""
    fields = columns()
    fields[1]["source_unit"] = "in"
    result = ingest(
        "sample.csv", b"part,length\nPanel,2", settings(output_standard={"columns": fields})
    )
    assert result["blocks"][0]["rows"][1][1] == "50.8 mm"
    assert result["source_blocks"][0]["rows"][1][1] == "2"
    other = ingest(
        "other.csv", b"month,revenue\n2026-01,100", settings(output_standard={"columns": fields})
    )
    assert other["warnings"] and other["blocks"][0]["rows"][0] == ["month", "revenue"]
    with pytest.raises(ValueError):
        ingest(
            "other.csv",
            b"month,revenue\n2026-01,100",
            settings(output_standard={"columns": fields, "table_scope": "all"}),
        )
    with pytest.raises(ValueError):
        ingest(
            "other.csv",
            b"part,length,extra\nPanel,2,sensitive",
            settings(output_standard={"columns": fields, "extra_columns": "reject"}),
        )


def test_schema_for_rich_tables():
    """DOCX, XLSX and sanitized HTML tables use the same schema as flat structured data."""
    from openpyxl import Workbook

    doc = Document()
    table = doc.add_table(rows=2, cols=2)
    table.cell(0, 0).text, table.cell(0, 1).text = "part", "length"
    table.cell(1, 0).text, table.cell(1, 1).text = "Panel", "4.25 in"
    document = io.BytesIO()
    doc.save(document)
    workbook = Workbook()
    workbook.active.append(["part", "length"])
    workbook.active.append(["Panel", "4.25 in"])
    sheet = io.BytesIO()
    workbook.save(sheet)
    html = b"<section><p>Before</p><table><tr><th>part</th><th>length</th></tr><tr><td>Panel</td><td>4.25 in</td></tr></table><p>After</p></section>"
    for name, data in [
        ("sample.docx", document.getvalue()),
        ("sample.xlsx", sheet.getvalue()),
        ("sample.html", html),
    ]:
        result = ingest(name, data, settings(output_standard={"columns": columns()}))
        tables = [block for block in result["blocks"] if block["kind"] == "table"]
        assert tables[0]["rows"][1] == ["Panel", "107.95 mm", ""]
    assert (
        result["html"].index("Before")
        < result["html"].index("<table>")
        < result["html"].index("After")
    )


def test_html_text_stays_inert_during_schema_expansion():
    """Decoding and splitting HTML text must not turn encoded markup into active elements."""
    result = ingest(
        "encoded.html",
        b"&lt;script&gt;alert(1)&lt;/script&gt;<table><tr><th>part</th><th>length</th></tr><tr><td>Panel</td><td>1 in</td></tr></table>",
        settings(output_standard={"columns": columns()}),
    )
    assert "<script>" not in result["html"]
    assert "&lt;script&gt;" in result["html"]


@pytest.mark.parametrize(
    "html",
    [
        b'<table><tr><th colspan="2">part</th></tr><tr><td>Panel</td><td>1 in</td></tr></table>',
        b"<table><tr><td><table><tr><td>part</td></tr></table></td></tr></table>",
    ],
)
def test_unsupported_merged_html_tables_fail_closed(html):
    """The sanitizer preserves harmless span metadata so schema validation can reject ambiguity."""
    with pytest.raises(ValueError):
        ingest("merged.html", html, settings(output_standard={"columns": columns()}))


@pytest.mark.parametrize(
    "standard",
    [
        {"accent": "red; background:url(https://evil.example)"},
        {"font": "url(evil)"},
        {"font_size": True},
        {"paper": "arbitrary"},
        {"default_export": "exe"},
        {"template": "{{execute()}}"},
        {"columns": [{"key": "a", "label": "A"}, {"key": "a", "label": "B"}]},
        {"columns": [{"key": "a", "label": "Shared"}, {"key": "b", "label": "shared"}]},
        {"columns": [{"key": "a", "label": "A", "source_unit": "kg", "dimension": "length"}]},
        {"columns": [{"key": "a", "label": "A", "aliases": [""]}]},
        {"section_titles": {"content": "Only one"}},
    ],
)
def test_safe_template_validation(standard):
    """No executable HTML/CSS/templates, coercive integer settings or ambiguous field contracts."""
    with pytest.raises(ValueError):
        settings(output_standard=standard)


def test_render_and_exports_use_snapshot():
    """A4 landscape, labels, font and export restrictions derive from the immutable conversion snapshot."""
    config = settings(
        output_standard={
            "name": "Fictional quality standard",
            "paper": "A4",
            "orientation": "landscape",
            "font": "serif",
            "font_size": 14,
            "accent": "#123456",
        }
    )
    config.output_standard.section_titles["content"] = "Approved <content>"
    result = ingest("sample.txt", b"Width 4.25 in", config)
    assert "Approved &lt;content&gt;" in result["html"] and "size:A4 landscape" in result["html"]
    docx = Document(io.BytesIO(export_document(result, "docx")))
    assert docx.sections[0].page_width > docx.sections[0].page_height
    assert docx.styles["Normal"].font.size.pt == 14
    pdf = PdfReader(io.BytesIO(export_document(result, "pdf")))
    assert float(pdf.pages[0].mediabox.width) > float(pdf.pages[0].mediabox.height)
    assert "107.95 mm" in pdf.pages[0].extract_text()
    config.output_standard.paper = "Letter"
    assert result["standard"]["output_standard"]["paper"] == "A4"
    result["standard"]["output_standard"].update(default_export="pdf", enforce_export=True)
    with pytest.raises(ValueError):
        export_document(result, "html")
    assert export_document(result, "pdf").startswith(b"%PDF")


def test_reapply_from_extracted_evidence_and_budget():
    """Repeated standard changes use original extracted values, not rounded prior output."""
    first = ingest("source.txt", b"Width 1 mm", settings(units={"length": "in"}))
    second = assemble(
        first["title"],
        first["source_blocks"],
        first["provenance"],
        settings(units={"length": "mm"}),
        [],
    )
    assert second["blocks"][0]["text"] == "Width 1 mm"
    assert first["blocks"][0]["text"] == "Width 0.03937 in"
    with pytest.raises(ValueError):
        assemble("over budget", [{"kind": "paragraph", "text": "x"}] * 3001, {}, settings(), [])


@pytest.fixture
def client(tmp_path):
    """Isolated real legacy accounts test server-side roles independently of browser controls."""
    with TestClient(create_app(tmp_path / "standards.sqlite", True)) as session:
        yield session


def login(client, role="admin"):
    """Authenticate actual seeded role and set its independently checked CSRF proof."""
    response = client.post(
        "/api/login",
        json={"workspace": "industrial", "username": role, "password": "workbench-demo"},
    )
    assert response.status_code == 200
    client.headers["x-csrf-token"] = response.json()["csrf"]


def test_authority_preview_history_restore(client):
    """Only the actual administrator can publish/preview/restore; stale saves never lose changes."""
    assert client.get("/api/standards/history").status_code == 401
    login(client)
    before = client.get("/api/config").json()["config"]
    draft = copy.deepcopy(before)
    draft["output_standard"]["name"] = "Fictional manufacturing standard"
    draft["output_standard"]["columns"] = columns()
    preview = client.post(
        "/api/standards/preview", json={"config": draft, "sample": "part,length\nPanel,4.25 in"}
    )
    assert preview.status_code == 200 and "107.95 mm" in preview.text
    assert client.get("/api/config").json()["config"] == before
    assert client.put("/api/config", json=draft).json()["revision"] == 2
    assert client.put("/api/config", json=draft).status_code == 409
    assert [item["revision"] for item in client.get("/api/standards/history").json()] == [2, 1]
    restored = client.post("/api/standards/restore", json={"revision": 1, "expected_revision": 2})
    assert restored.status_code == 200 and restored.json()["revision"] == 3
    assert restored.json()["output_standard"]["name"] == before["output_standard"]["name"]
    assert (
        client.post(
            "/api/standards/restore", json={"revision": 1, "expected_revision": 2}
        ).status_code
        == 409
    )
    assert (
        client.post(
            "/api/standards/restore", json={"revision": 999, "expected_revision": 3}
        ).status_code
        == 404
    )
    login(client, "employee")
    client.headers["X-KBW-View"] = "admin"
    for path, method, body in [
        ("config", "put", draft),
        ("standards/preview", "post", {"config": draft, "sample": "part,length\nPanel,4 in"}),
        ("standards/restore", "post", {"revision": 1, "expected_revision": 3}),
    ]:
        assert getattr(client, method)("/api/" + path, json=body).status_code == 403
    assert client.get("/api/standards/history").status_code == 403


def test_current_copy_and_mixed_revision_merge(client):
    """Re-standardization preserves originals, ACLs and sales while compilations use one current unit contract."""
    login(client)
    config = client.get("/api/config").json()["config"]
    config["units"]["length"] = "in"
    client.put("/api/config", json=config).raise_for_status()
    first = client.post("/api/import", files={"file": ("sample.txt", b"Width 1 mm")}).json()["id"]
    original = client.get("/api/documents/" + first).json()
    config = client.get("/api/config").json()["config"]
    config["units"]["length"] = "mm"
    config["output_standard"].update(
        name="Current metric", default_export="pdf", enforce_export=True
    )
    client.put("/api/config", json=config).raise_for_status()
    count_before = client.get("/api/report").json()["quantity"]
    copy_id = client.post(f"/api/documents/{first}/standardize").json()["id"]
    assert first != copy_id
    copied = client.get("/api/documents/" + copy_id).json()
    assert copied["blocks"][0]["text"] == "Width 1 mm"
    assert client.get("/api/documents/" + first).json() == original
    assert client.get(f"/api/documents/{copy_id}/export/html").status_code == 422
    assert client.get(f"/api/documents/{copy_id}/export/pdf").content.startswith(b"%PDF")
    combined = client.post(
        "/api/merge", json={"ids": [first, copy_id], "title": "Current standard pack"}
    )
    assert combined.status_code == 200
    document = client.get("/api/documents/" + combined.json()["id"]).json()
    assert all(record["unit"] == "mm" for record in document["measurements"])
    assert client.post(f"/api/documents/{combined.json()['id']}/standardize").status_code == 200
    assert client.get("/api/report").json()["quantity"] == count_before
    assert client.get("/api/report/export/pdf").content.startswith(b"%PDF")
    assert client.get("/api/report/export/html").status_code == 422
    login(client, "customer")
    assert client.get("/api/documents/" + copy_id).status_code == 404
    assert client.post(f"/api/documents/{copy_id}/standardize").status_code == 403


def test_legacy_config_migration_is_idempotent(tmp_path):
    """Existing schema-one accounts retain data/configuration and get their actual active history snapshot."""
    path = tmp_path / "old.sqlite"
    initialize(path, False)
    old = settings().model_dump()
    old.pop("output_standard")
    old["revision"] = 7
    with connect(path) as db:
        db.execute("UPDATE workspaces SET config=? WHERE id='industrial'", (json.dumps(old),))
        db.execute("DROP TABLE config_history")
    initialize(path, False)
    initialize(path, False)
    with connect(path) as db:
        rows = db.execute("SELECT * FROM config_history WHERE workspace='industrial'").fetchall()
        assert len(rows) == 1 and rows[0]["revision"] == 7
        assert (
            json.loads(
                db.execute("SELECT config FROM workspaces WHERE id='industrial'").fetchone()[0]
            )
            == old
        )


def test_simultaneous_publication_has_one_winner(client):
    """Two editors publishing one base revision cannot overwrite each other or duplicate history."""
    from concurrent.futures import ThreadPoolExecutor

    login(client)
    draft = client.get("/api/config").json()["config"]
    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(
            pool.map(lambda _: client.put("/api/config", json=draft).status_code, range(2))
        )
    assert sorted(outcomes) == [200, 409]
    assert [row["revision"] for row in client.get("/api/standards/history").json()] == [2, 1]


def test_sales_aliases_remain_input_contract(client):
    """Presentation remapping never changes sales input meaning or replays accounting on a copy."""
    login(client)
    config = client.get("/api/config").json()["config"]
    config["output_standard"]["columns"] = [
        {"key": "item_id", "label": "Product", "aliases": ["product"]}
    ]
    assert client.put("/api/config", json=config).status_code == 200
    before = client.get("/api/report").json()["quantity"]
    response = client.post(
        "/api/import",
        files={
            "file": (
                "sale.csv",
                b"product,customer,month,quantity,revenue_cents\nMC-240,north,2026-01,2,100",
            )
        },
        data={"dataset": "true"},
    )
    assert response.status_code == 200
    assert client.get("/api/report").json()["quantity"] == before + 2
    assert client.post(f"/api/documents/{response.json()['id']}/standardize").status_code == 200
    assert client.get("/api/report").json()["quantity"] == before + 2


def test_identical_bytes_with_different_formats_are_not_wrongly_deduplicated(client):
    """Source identity alone does not imply identical parser semantics: TXT and CSV must differ."""
    login(client)
    payload = b"part,length\nPanel,4.25 in"
    text = client.post("/api/import", files={"file": ("same.txt", payload)}).json()["id"]
    csv = client.post("/api/import", files={"file": ("same.csv", payload)}).json()["id"]
    assert text != csv
    assert client.get("/api/documents/" + text).json()["blocks"][0]["kind"] == "paragraph"
    assert client.get("/api/documents/" + csv).json()["blocks"][0]["kind"] == "table"
    assert client.get(f"/api/documents/{text}/export/csv").status_code == 422
    assert client.get(f"/api/documents/{csv}/export/csv").status_code == 200
