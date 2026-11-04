# @index-begin
# @symbol function/class: library_client L51
# @symbol variable/parameter: tmp_path L51
# @symbol variable/parameter: response L54
# @symbol variable/parameter: library_client L62
# @symbol function/class: test_literal_search_scoped_facets_and_filters L62
# @symbol variable/parameter: client L64
# @symbol variable/parameter: payload L65
# @symbol variable/parameter: identifier L66
# @symbol variable/parameter: filters L69
# @symbol variable/parameter: records L77
# @symbol variable/parameter: row L78
# @symbol variable/parameter: page1 L91
# @symbol variable/parameter: page2 L92
# @symbol function/class: test_facets_counts_and_downloads_never_broaden_roles L98
# @symbol variable/parameter: login L107
# @symbol variable/parameter: result L112
# @symbol variable/parameter: suffix L117
# @symbol function/class: test_hidden_fields_layout_and_authorized_file_preview L128
# @symbol variable/parameter: config L131
# @symbol variable/parameter: before L132
# @symbol variable/parameter: draft L155
# @symbol variable/parameter: document L162
# @symbol variable/parameter: pdf L167
# @symbol variable/parameter: page L168
# @symbol variable/parameter: text L168
# @symbol function/class: test_old_defaults_and_invalid_layout_are_not_silently_accepted L181
# @symbol variable/parameter: settings L188
# @index-end
"""Jason Stys: genuine API library, role, field-binding and draft-preview regressions.

Functions/variables and exact lines: docs/code-index.md. Synthetic accounts only;
assertions use persisted outputs and independent expected values, not UI labels.
"""

import io
import json

import pytest
from docx import Document
from fastapi.testclient import TestClient
from pypdf import PdfReader

from server.app import create_app
from server.conversion import ingest
from server.exports import export_document
from server.models import OutputStandard, WorkspaceConfig


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
