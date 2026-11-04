# @index-begin
# @symbol variable/parameter: ROOT L67
# @symbol variable/parameter: CASES L68
# @symbol variable/parameter: extension L71
# @symbol variable/parameter: scenario L71
# @symbol function/class: source L71
# @symbol variable/parameter: rows L73
# @symbol variable/parameter: output L74
# @symbol variable/parameter: text L76
# @symbol variable/parameter: workbook L93
# @symbol variable/parameter: row L94
# @symbol variable/parameter: path L100
# @symbol variable/parameter: table L103
# @symbol variable/parameter: case L113
# @symbol function/class: test_real_industry_normalization_and_exports L115
# @symbol variable/parameter: config L117
# @symbol variable/parameter: result L134
# @symbol variable/parameter: block L135
# @symbol variable/parameter: tables L135
# @symbol variable/parameter: format_name L140
# @symbol variable/parameter: payload L141
# @symbol variable/parameter: document L143
# @symbol variable/parameter: actual L144
# @symbol variable/parameter: cell L144
# @symbol variable/parameter: pdf L149
# @symbol variable/parameter: page L150
# @symbol variable/parameter: target L152
# @symbol variable/parameter: value L167
# @symbol function/class: test_profile_publication_upload_search_download_and_staff_boundary L172
# @symbol variable/parameter: tmp_path L172
# @symbol variable/parameter: client L174
# @symbol variable/parameter: profile L175
# @symbol variable/parameter: login L176
# @symbol variable/parameter: imported L189
# @symbol variable/parameter: identifier L195
# @symbol variable/parameter: persisted L196
# @symbol variable/parameter: records L201
# @index-end
"""Jason Stys: independent realistic industry oracles across rich source/export formats.

Functions/variables and exact lines: docs/code-index.md. All companies and records
are fictional. Numeric expected values are authored independently, not calculated
with the conversion function under test. Test artifacts contain synthetic data only.
"""

import csv
import io
import json
from html import escape
from pathlib import Path

import pytest
from bs4 import BeautifulSoup
from docx import Document
from fastapi.testclient import TestClient
from openpyxl import Workbook
from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

from server.app import create_app
from server.conversion import ingest
from server.exports import export_document
from server.models import WorkspaceConfig

ROOT = Path(__file__).resolve().parents[2]
CASES = json.loads((ROOT / "examples/industry-cases.json").read_text(encoding="utf-8"))


def source(scenario, extension):
    """Create tiny genuine inputs using independent libraries and inert synthetic content."""
    rows = [scenario["headers"], *scenario["rows"]]
    output = io.BytesIO()
    if extension in {"csv", "tsv"}:
        text = io.StringIO(newline="")
        csv.writer(text, delimiter="\t" if extension == "tsv" else ",").writerows(rows)
        return text.getvalue().encode()
    if extension == "json":
        return json.dumps(
            [dict(zip(scenario["headers"], row, strict=True)) for row in scenario["rows"]]
        ).encode()
    if extension in {"html", "htm"}:
        return (
            "<table>"
            + "".join(
                "<tr>" + "".join("<td>" + escape(cell) + "</td>" for cell in row) + "</tr>"
                for row in rows
            )
            + "</table>"
        ).encode()
    if extension == "xlsx":
        workbook = Workbook()
        for row in rows:
            workbook.active.append(row)
        workbook.save(output)
        workbook.close()
        return output.getvalue()
    if extension == "docx":
        path = ROOT / "examples/industry-inputs" / (scenario["profile"] + ".docx")
        assert path.exists(), "Run node scripts/industry_fixtures.mjs before the industry matrix"
        return path.read_bytes()
    table = Table(rows, colWidths=[480 / len(rows[0])] * len(rows[0]))
    table.setStyle(
        TableStyle(
            [("GRID", (0, 0), (-1, -1), 0.5, colors.black), ("FONTSIZE", (0, 0), (-1, -1), 8)]
        )
    )
    SimpleDocTemplate(output, pagesize=letter).build([table])
    return output.getvalue()


@pytest.mark.parametrize("scenario", CASES, ids=[case["profile"] for case in CASES])
@pytest.mark.parametrize("extension", ["csv", "tsv", "json", "html", "htm", "xlsx", "docx", "pdf"])
def test_real_industry_normalization_and_exports(scenario, extension):
    """Check normalized rows, omitted clutter, original evidence and every supported export."""
    config = WorkspaceConfig(
        title=scenario["company"],
        profile=scenario["profile"],
        units=scenario["units"],
        sections=["content", "measurements"],
        output_standard={
            "name": scenario["company"] + " standard",
            "columns": scenario["fields"],
            "extra_columns": "omit",
            "paper": "A4",
            "orientation": "landscape" if scenario["profile"] == "laboratory" else "portrait",
            "margin_mm": 25,
            "header_text": scenario["company"],
            "footer_text": "Synthetic evidence - human review required",
            "page_numbers": True,
        },
    )
    result = ingest("synthetic." + extension, source(scenario, extension), config)
    tables = [block for block in result["blocks"] if block["kind"] == "table"]
    assert len(tables) == 1 and tables[0]["rows"] == scenario["expected"]
    assert result["provenance"]["conversion_path"] == [extension, "html"]
    assert scenario["rows"][0][-1] not in result["html"]
    assert any(scenario["rows"][0][-1] in str(block) for block in result["source_blocks"])
    for format_name in ("html", "json", "md", "csv", "docx", "pdf"):
        payload = export_document(result, format_name)
        if format_name == "docx":
            document = Document(io.BytesIO(payload))
            actual = [[cell.text for cell in row.cells] for row in document.tables[0].rows]
            assert actual[1:] == scenario["expected"][1:]
            assert abs(document.sections[0].left_margin.mm - 25) < 0.1
            text = " ".join(cell.text for row in document.tables[0].rows for cell in row.cells)
        elif format_name == "pdf":
            pdf = PdfReader(io.BytesIO(payload))
            text = " ".join(page.extract_text() for page in pdf.pages)
            if extension == "csv":
                target = ROOT / "artifacts/industry-outputs"
                target.mkdir(parents=True, exist_ok=True)
                (target / (scenario["profile"] + ".pdf")).write_bytes(payload)
                (target / (scenario["profile"] + ".docx")).write_bytes(
                    export_document(result, "docx")
                )
        elif format_name == "html":
            text = BeautifulSoup(payload, "html.parser").get_text(" ", strip=True)
        elif format_name == "json":
            assert json.loads(payload)["blocks"][0 if extension not in {"docx", "xlsx"} else 1][
                "kind"
            ] in {"table", "heading"}
            text = json.loads(payload)["text"]
        else:
            text = payload.decode("utf-8-sig")
        for value in scenario["expected"][1]:
            assert value in text


@pytest.mark.parametrize("scenario", CASES, ids=[case["profile"] for case in CASES])
def test_profile_publication_upload_search_download_and_staff_boundary(tmp_path, scenario):
    """Each industry traverses genuine sessions, configuration, workers, storage and scoped exports."""
    with TestClient(create_app(tmp_path / "industry.sqlite", demo=True)) as client:
        profile = scenario["profile"]
        login = client.post(
            "/api/login",
            json={"workspace": profile, "username": "admin", "password": "workbench-demo"},
        )
        assert login.status_code == 200
        client.headers["x-csrf-token"] = login.json()["csrf"]
        config = client.get("/api/config").json()["config"]
        config["units"] = scenario["units"]
        config["output_standard"].update(
            columns=scenario["fields"], extra_columns="omit", default_export="docx"
        )
        assert client.put("/api/config", json=config).status_code == 200
        payload = source(scenario, "xlsx")
        imported = client.post(
            "/api/import",
            files={"file": ("synthetic-inspection.xlsx", payload)},
            data={"category": "Synthetic inspection"},
        )
        assert imported.status_code == 200, imported.text
        identifier = imported.json()["id"]
        persisted = client.get("/api/documents/" + identifier).json()
        assert (
            next(block["rows"] for block in persisted["blocks"] if block["kind"] == "table")
            == scenario["expected"]
        )
        records = client.get(
            "/api/library",
            params={
                "category": "Synthetic inspection",
                "source_format": "xlsx",
                "field": scenario["expected"][0][1],
                "value": scenario["expected"][1][1],
            },
        )
        assert records.status_code == 200 and [row["id"] for row in records.json()["items"]] == [
            identifier
        ]
        assert client.get("/api/documents/" + identifier + "/source").content == payload
        output = client.get("/api/documents/" + identifier + "/export/docx")
        assert output.status_code == 200
        assert (
            Document(io.BytesIO(output.content)).tables[0].cell(1, 1).text
            == scenario["expected"][1][1]
        )
        client.post("/api/logout")
        login = client.post(
            "/api/login",
            json={"workspace": profile, "username": "employee", "password": "workbench-demo"},
        )
        client.headers["x-csrf-token"] = login.json()["csrf"]
        assert client.get("/api/documents/" + identifier).status_code == 200
        assert client.get("/api/documents/" + identifier + "/export/docx").status_code == 200
        assert client.put("/api/config", json=config).status_code == 403
        assert (
            client.post(
                "/api/standards/preview-file",
                files={"file": ("source.xlsx", payload)},
                data={"config": json.dumps(config)},
            ).status_code
            == 403
        )
