# @index-begin
# @symbol function/class: library_client L87
# @symbol variable/parameter: tmp_path L87
# @symbol variable/parameter: library_client L98
# @symbol function/class: test_literal_search_scoped_facets_and_filters L98
# @symbol variable/parameter: client L100
# @symbol variable/parameter: payload L101
# @symbol variable/parameter: identifier L102
# @symbol variable/parameter: filters L105
# @symbol variable/parameter: page1 L127
# @symbol variable/parameter: page2 L128
# @symbol function/class: test_facets_counts_and_downloads_never_broaden_roles L134
# @symbol variable/parameter: login L143
# @symbol variable/parameter: result L148
# @symbol variable/parameter: suffix L153
# @symbol function/class: test_hidden_fields_layout_and_authorized_file_preview L164
# @symbol variable/parameter: config L167
# @symbol variable/parameter: before L168
# @symbol variable/parameter: draft L191
# @symbol variable/parameter: document L198
# @symbol variable/parameter: pdf L203
# @symbol variable/parameter: page L204
# @symbol variable/parameter: text L204
# @symbol function/class: test_old_defaults_and_invalid_layout_are_not_silently_accepted L217
# @symbol variable/parameter: settings L224
# @symbol variable/parameter: expected L281
# @symbol variable/parameter: maximum L281
# @symbol variable/parameter: minimum L281
# @symbol function/class: test_numeric_cell_contract L281
# @symbol variable/parameter: unit L281
# @symbol variable/parameter: value L281
# @symbol function/class: test_numeric_search_binds_one_cell_and_saved_units L286
# @symbol variable/parameter: first L289
# @symbol variable/parameter: item L303
# @symbol variable/parameter: change L306
# @symbol variable/parameter: second L311
# @symbol variable/parameter: records L316
# @symbol function/class: test_scientific_notation_survives_import_search_and_export L323
# @symbol variable/parameter: response L326
# @symbol variable/parameter: found L333
# @symbol variable/parameter: query L353
# @symbol function/class: test_invalid_numeric_queries_are_explained L353
# @symbol variable/parameter: monkeypatch L358
# @symbol function/class: test_bundle_manifest_order_policy_and_scope L358
# @symbol variable/parameter: archive L373
# @symbol variable/parameter: manifest L374
# @symbol variable/parameter: row L384
# @symbol variable/parameter: p L392
# @symbol variable/parameter: visible L400
# @symbol variable/parameter: app_module L408
# @symbol function/class: forbidden_generation L410
# @symbol function/class: test_bundle_limits_and_safe_flat_names L420
# @symbol variable/parameter: ids L424
# @symbol variable/parameter: n L424
# @symbol variable/parameter: rows L435
# @symbol variable/parameter: entry L439
# @symbol variable/parameter: char L440
# @symbol variable/parameter: invalid L441
# @index-end
"""Jason Stys: genuine API library, role, field-binding and draft-preview regressions.

Functions/variables and exact lines: docs/code-index.md. Synthetic accounts only;
assertions use persisted outputs and independent expected values, not UI labels.
"""

import hashlib
import importlib
import io
import json
import threading
import zipfile

import pytest
from docx import Document
from fastapi.testclient import TestClient
from pypdf import PdfReader

from server.app import create_app
from server.bundles import create_bundle
from server.conversion import ingest
from server.exports import export_document
from server.models import OutputStandard, WorkspaceConfig
from server.quantitative import in_range


@pytest.fixture
def library_client(tmp_path):
    """Run a disposable database and real session/CSRF authentication boundary."""
    with TestClient(create_app(tmp_path / "library.sqlite", demo=True)) as client:
        response = client.post(
            "/api/login",
            json={"workspace": "industrial", "username": "admin", "password": "workbench-demo"},
        )
        client.headers["x-csrf-token"] = response.json()["csrf"]
        yield client


def test_literal_search_scoped_facets_and_filters(library_client):
    """Round-trip real multipart source, canonical content and exact correlated field searches."""
    client = library_client
    payload = b"part,width,mass\nFictional Panel,4.25 in,2.2 lb\nFictional Bracket,8.2 cm,500 g"
    identifier = client.post(
        "/api/import", files={"file": ("factory.csv", payload)}, data={"category": "Metrology"}
    ).json()["id"]
    for filters in (
        {"q": "107.95 mm"},
        {"category": "Metrology", "source_format": "csv", "kind": "table", "dimension": "length"},
        {"field": "width", "value": "107.95 mm"},
        {"field": "part", "value": "Fictional Panel"},
    ):
        response = client.get("/api/library", params={"category": "Metrology", **filters})
        assert response.status_code == 200, response.text
        records = response.json()
        assert [row["id"] for row in records["items"]] == [identifier]
        assert "result" not in records["items"][0] and "html" not in records["items"][0]
        assert records["items"][0]["standard_format"] == "html"
        assert "width" in records["facets"]["fields"]
    for filters in ({"field": "mass", "value": "107.95 mm"}, {"q": "%"}, {"q": "' OR 1=1 --"}):
        assert client.get("/api/library", params=filters).json()["total"] == 0
    assert client.get("/api/library", params={"value": "107.95"}).status_code == 422
    assert (
        client.get("/api/library", params={"sort": "created; DROP TABLE documents"}).status_code
        == 422
    )
    assert client.get("/api/library", params={"limit": 201}).status_code == 422
    assert client.get("/api/library", params={"unrecognized": "no"}).status_code == 422
    page1 = client.get("/api/library", params={"limit": 3}).json()
    page2 = client.get("/api/library", params={"limit": 3, "offset": 3}).json()
    assert page1["total"] == page2["total"] == 10
    assert not {row["id"] for row in page1["items"]} & {row["id"] for row in page2["items"]}
    assert client.get("/api/library", params={"offset": 200}).json()["items"] == []


def test_facets_counts_and_downloads_never_broaden_roles(library_client):
    """A customer's search cannot reveal hidden categories, data, counts or source/export bytes."""
    client = library_client
    identifier = client.post(
        "/api/import",
        files={"file": ("hidden.csv", b"classified_key\nprivate-secret")},
        data={"category": "HiddenCategory"},
    ).json()["id"]
    client.post("/api/logout")
    login = client.post(
        "/api/login",
        json={"workspace": "industrial", "username": "customer", "password": "workbench-demo"},
    )
    client.headers["x-csrf-token"] = login.json()["csrf"]
    result = client.get("/api/library", params={"workspace": "renewable"}).json()
    assert result["total"] == 5
    assert "HiddenCategory" not in result["facets"]["categories"]
    assert "classified_key" not in result["facets"]["fields"]
    assert client.get("/api/library?q=private-secret").json()["total"] == 0
    for suffix in ("", "/preview", "/source", "/export/docx"):
        assert client.get("/api/documents/" + identifier + suffix).status_code == 404
    assert client.post("/api/import", files={"file": ("no.txt", b"no")}).status_code == 403
    assert (
        client.post(
            "/api/standards/preview-file", files={"file": ("no.txt", b"no")}, data={"config": "{}"}
        ).status_code
        == 403
    )


def test_hidden_fields_layout_and_authorized_file_preview(library_client):
    """Draft previews neither save standards nor insert records; exclusion is explicit, not redaction."""
    client = library_client
    config = client.get("/api/config").json()["config"]
    before = client.get("/api/library").json()["total"]
    config["output_standard"].update(
        columns=[
            {"key": "item", "label": "Part", "aliases": ["part"]},
            {"key": "width", "label": "Width", "dimension": "length"},
            {"key": "note", "label": "Supplier note", "enabled": False},
        ],
        extra_columns="omit",
        margin_mm=25,
        alignment="right",
        line_spacing=1.5,
        paragraph_after_pt=12,
        header_text="Fictional Harbor Manufacturing",
        footer_text="Synthetic inspection - review required",
        page_numbers=True,
    )
    payload = b"part,width,note,obsolete\nPanel,4.25 in,retain original only,old tag"
    result = client.post(
        "/api/standards/preview-file",
        files={"file": ("inspection.csv", payload)},
        data={"config": json.dumps(config)},
    )
    assert result.status_code == 200, result.text
    draft = result.json()
    assert draft["blocks"][0]["rows"] == [["item", "width"], ["Panel", "107.95 mm"]]
    assert "retain original only" not in draft["html"]
    assert draft["source_blocks"][0]["rows"][1][2] == "retain original only"
    assert "margin:25mm" in draft["html"] and "text-align:right" in draft["html"]
    assert client.get("/api/library").json()["total"] == before
    assert client.get("/api/config").json()["config"]["revision"] == config["revision"]
    document = Document(io.BytesIO(export_document(draft, "docx")))
    assert abs(document.sections[0].left_margin.mm - 25) < 0.1
    assert document.sections[0].header.paragraphs[0].text == "Fictional Harbor Manufacturing"
    assert "PAGE" in document.sections[0].footer._element.xml
    assert document.styles["Normal"].paragraph_format.line_spacing == 1.5
    pdf = PdfReader(io.BytesIO(export_document(draft, "pdf")))
    text = " ".join(page.extract_text() for page in pdf.pages)
    assert "107.95 mm" in text and "Page 1" in text and "Fictional Harbor" in text
    assert "retain original only" not in text
    assert (
        client.post(
            "/api/standards/preview-file",
            files={"file": ("bad.exe", b"no")},
            data={"config": json.dumps(config)},
        ).status_code
        == 415
    )


def test_old_defaults_and_invalid_layout_are_not_silently_accepted():
    """Old stored standard JSON gains safe defaults; unknown code/layout and empty active schemas fail."""
    assert OutputStandard.model_validate({}).margin_mm == 20
    assert (
        WorkspaceConfig(title="Legacy company", profile="industrial").output_standard.line_spacing
        == 1.15
    )
    for settings in (
        {"margin_mm": 0},
        {"line_spacing": -2},
        {"header_text": "x" * 121},
        {"alignment": "url(javascript:evil)"},
        {"columns": [{"key": "item", "label": "Item", "enabled": False}]},
    ):
        with pytest.raises(ValueError):
            OutputStandard.model_validate(settings)
    config = WorkspaceConfig(
        title="Fictional company",
        profile="industrial",
        units={},
        output_standard={
            "columns": [
                {"key": "item", "label": "Item"},
                {"key": "width", "label": "Width", "dimension": "length", "enabled": False},
            ],
            "extra_columns": "omit",
        },
    )
    result = ingest("sample.csv", b"item,width\nPanel,4.25 in", config)
    assert result["blocks"][0]["rows"] == [["item"], ["Panel"]]


@pytest.mark.parametrize(
    ("value", "minimum", "maximum", "unit", "expected"),
    [
        ("4.25 in", "107.95", "107.95", "mm", 1),
        ("8.2 cm", "80", "83", "mm", 1),
        ("2.2 lb", "0.997903", "0.997903", "kg", 1),
        ("32 F", "0", "0", "C", 1),
        ("273.15 K", "0", "0", "C", 1),
        ("100 C", "212", "212", "F", 1),
        ("101 kPa", "1", "1.1", "bar", 1),
        ("12 mV", ".012", ".012", "V", 1),
        ("1000 Wh", "1", "1", "kWh", 1),
        (0, "0", "0", "", 1),
        ("1e-7", "0", "0.000001", "", 1),
        ("-5", None, "0", "", 1),
        ("4.25 in", "108", None, "mm", 0),
        ("3 mm", None, "4", "", 0),
        ("3", "0", None, "mm", 0),
        ("3 kg", "0", None, "mm", 0),
        ("3 xyz", "0", None, "mm", 0),
        ("-274 C", "0", None, "K", 0),
        (None, None, "0", "", 0),
        (True, "0", None, "", 0),
        ("NaN", "0", None, "", 0),
        ("Infinity", "0", None, "", 0),
        ("1e300", "0", None, "", 0),
        ("1000000000000001", "0", None, "", 0),
        ("1 + 2", "0", None, "", 0),
        ("length 3 mm", "0", None, "mm", 0),
        ("0 or absent", "0", "0", "", 0),
    ],
)
def test_numeric_cell_contract(value, minimum, maximum, unit, expected):
    """Independent physical values; malformed/missing cells never become zero or expressions."""
    assert in_range(value, minimum, maximum, unit) == expected


def test_numeric_search_binds_one_cell_and_saved_units(library_client):
    """Find comparable measurements across saved revisions, never across unrelated rows or fields."""
    client = library_client
    first = client.post(
        "/api/import",
        files={
            "file": ("first.csv", b"part,width,mass\nPanel,4.25 in,2.2 lb\nBracket,8.2 cm,500 g")
        },
        data={"category": "NumericStudy"},
    ).json()["id"]
    filters = {
        "category": "NumericStudy",
        "field": "width",
        "minimum": "100",
        "maximum": "110",
        "unit": "mm",
    }
    assert [item["id"] for item in client.get("/api/library", params=filters).json()["items"]] == [
        first
    ]
    for change in ({"value": "82"}, {"field": "mass"}, {"unit": "kg"}):
        assert client.get("/api/library", params={**filters, **change}).json()["total"] == 0
    config = client.get("/api/config").json()["config"]
    config["units"]["length"] = "cm"
    client.put("/api/config", json=config).raise_for_status()
    second = client.post(
        "/api/import",
        files={"file": ("second.csv", b"part,width\nPanel2,4.25 in")},
        data={"category": "NumericStudy"},
    ).json()["id"]
    records = client.get("/api/library", params=filters).json()["items"]
    assert {item["id"] for item in records} == {first, second}
    assert {item["standard_revision"] for item in records} == {1, 2}
    assert "107.95 mm" in client.get(f"/api/documents/{first}").json()["text"]
    assert "10.795 cm" in client.get(f"/api/documents/{second}").json()["text"]


def test_scientific_notation_survives_import_search_and_export(library_client):
    """A laboratory's 5e-3 V is exactly 5 mV, never a converted exponent suffix."""
    client = library_client
    response = client.post(
        "/api/import", files={"file": ("probe.csv", b"part,signal\nProbe,5e-3 V")}
    )
    response.raise_for_status()
    identifier = response.json()["id"]
    document = client.get(f"/api/documents/{identifier}").json()
    assert document["blocks"][0]["rows"][1] == ["Probe", "0.005 V"]
    found = client.get(
        "/api/library", params={"field": "signal", "minimum": "4", "maximum": "6", "unit": "mV"}
    ).json()
    assert [row["id"] for row in found["items"]] == [identifier]
    assert "0.005 V" in client.get(f"/api/documents/{identifier}/export/html").text


@pytest.mark.parametrize(
    "query",
    [
        {"minimum": "1"},
        {"field": "width", "minimum": "3", "maximum": "2"},
        {"field": "width", "minimum": "NaN"},
        {"field": "width", "maximum": "Infinity"},
        {"field": "width", "minimum": "1e16"},
        {"field": "width", "minimum": "1", "unit": "abc"},
        {"field": "width", "unit": "mm"},
        {"field": "width", "minimum": "0.0000000000001"},
    ],
)
def test_invalid_numeric_queries_are_explained(library_client, query):
    """Reject unsupported precision, units and ambiguous ranges before issuing SQL."""
    assert library_client.get("/api/library", params=query).status_code == 422


def test_bundle_manifest_order_policy_and_scope(library_client, monkeypatch):
    """Download only authorized standardized bytes, using each immutable saved output policy."""
    client = library_client
    first = client.post(
        "/api/import", files={"file": ("first.csv", b"part,width\nPanel,4.25 in")}
    ).json()["id"]
    config = client.get("/api/config").json()["config"]
    config["output_standard"]["default_export"] = "docx"
    client.put("/api/config", json=config).raise_for_status()
    second = client.post(
        "/api/import", files={"file": ("second.txt", b"Fictional inspection: 8.2 cm")}
    ).json()["id"]
    response = client.post("/api/exports/bundle", json={"ids": [second, first]})
    assert response.status_code == 200, response.text
    assert response.headers["content-type"] == "application/zip"
    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        manifest = json.loads(archive.read("manifest.json"))
        assert manifest["schema"] == "kbw-standardized-bundle/v1"
        assert manifest["originals_included"] is False
        assert [row["id"] for row in manifest["documents"]] == [second, first]
        assert [row["format"] for row in manifest["documents"]] == ["docx", "html"]
        assert {row["standard_revision"] for row in manifest["documents"]} == {1, 2}
        assert set(archive.namelist()) == {
            "manifest.json",
            *(row["file"] for row in manifest["documents"]),
        }
        for row in manifest["documents"]:
            payload = archive.read(row["file"])
            assert row["sha256"] == hashlib.sha256(payload).hexdigest()
            assert row["bytes"] == len(payload)
            assert len(row["standard_sha256"]) == 64
            assert "/" not in row["file"] and "\\" not in row["file"]
        assert "107.95 mm" in archive.read(manifest["documents"][1]["file"]).decode()
        document = Document(io.BytesIO(archive.read(manifest["documents"][0]["file"])))
        assert "82 mm" in " ".join(p.text for p in document.paragraphs)
    client.headers.pop("x-csrf-token")
    assert client.post("/api/exports/bundle", json={"ids": [first]}).status_code == 403
    login = client.post(
        "/api/login",
        json={"workspace": "industrial", "username": "customer", "password": "workbench-demo"},
    )
    client.headers["x-csrf-token"] = login.json()["csrf"]
    visible = client.get("/api/library").json()["items"][0]["id"]
    assert client.post("/api/exports/bundle", json={"ids": [visible]}).status_code == 200
    assert (
        client.get(
            "/api/library", params={"field": "width", "minimum": "100", "unit": "mm"}
        ).json()["total"]
        == 0
    )
    app_module = importlib.import_module("server.app")

    def forbidden_generation(rows):
        """Prove that mixed unauthorized selections are rejected before any output work."""
        pytest.fail("Unauthorized selection reached file generation")

    monkeypatch.setattr(app_module, "create_bundle", forbidden_generation)
    assert client.post("/api/exports/bundle", json={"ids": [visible, first]}).status_code == 404
    client.post("/api/logout")
    assert client.post("/api/exports/bundle", json={"ids": [visible]}).status_code == 401


def test_bundle_limits_and_safe_flat_names(library_client, monkeypatch):
    """Bound work before and during generation; untrusted titles cannot create extraction paths."""
    client = library_client
    identifier = client.get("/api/library").json()["items"][0]["id"]
    for ids in ([], [identifier, identifier], [str(n) for n in range(13)], ["a" * 81]):
        assert client.post("/api/exports/bundle", json={"ids": ids}).status_code == 422
    monkeypatch.setattr("server.bundles.MAX_BUNDLE_BYTES", 1)
    assert client.post("/api/exports/bundle", json={"ids": [identifier]}).status_code == 413
    monkeypatch.setattr("server.bundles.MAX_BUNDLE_BYTES", 32 * 1024 * 1024)
    app_module = importlib.import_module("server.app")
    monkeypatch.setattr(app_module, "BUNDLE_SLOTS", threading.BoundedSemaphore(0))
    assert client.post("/api/exports/bundle", json={"ids": [identifier]}).status_code == 429
    result = ingest(
        "safe.txt", b"Synthetic test 4.25 in", WorkspaceConfig(title="Sample", profile="industrial")
    )
    rows = [
        {"id": "safe", "title": "../../CON\\sensitive:report.txt", "result": json.dumps(result)}
    ]
    with zipfile.ZipFile(io.BytesIO(create_bundle(rows))) as archive:
        entry = json.loads(archive.read("manifest.json"))["documents"][0]["file"]
        assert entry.startswith("01-") and not any(char in entry for char in "/\\:")
    for invalid in ([], rows * 13):
        with pytest.raises(ValueError):
            create_bundle(invalid)
