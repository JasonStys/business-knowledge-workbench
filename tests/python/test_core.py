# @index-begin
# @symbol variable/parameter: EXAMPLES L55
# @symbol variable/parameter: expected L73
# @symbol variable/parameter: source L73
# @symbol variable/parameter: target L73
# @symbol function/class: test_units L73
# @symbol variable/parameter: value L73
# @symbol function/class: test_bad_units L91
# @symbol function/class: test_provenance_and_ambiguity L97
# @symbol variable/parameter: records L99
# @symbol variable/parameter: text L99
# @symbol variable/parameter: spaced L105
# @symbol variable/parameter: settings L121
# @symbol function/class: test_config_rejection L121
# @symbol variable/parameter: filename L141
# @symbol function/class: test_fixtures L141
# @symbol variable/parameter: result L143
# @symbol variable/parameter: block L152
# @symbol variable/parameter: data L172
# @symbol variable/parameter: name L172
# @symbol function/class: test_text_types L172
# @symbol function/class: test_reject_bad_files L192
# @symbol function/class: test_zip_and_table_limits L198
# @symbol variable/parameter: output L200
# @symbol variable/parameter: archive L201
# @symbol variable/parameter: format_name L211
# @symbol function/class: test_exports L211
# @symbol variable/parameter: payload L218
# @symbol function/class: test_rich_exports L230
# @symbol function/class: test_ai_contracts L243
# @symbol variable/parameter: context L245
# @symbol variable/parameter: adapter L246
# @symbol variable/parameter: answer L247
# @symbol variable/parameter: endpoint L257
# @symbol function/class: test_large_image L268
# @index-end
"""Conversion, unit, export and AI contract regression coverage. Index: docs/code-index.md."""

import io
import json
import zipfile
from pathlib import Path

import pytest
from defusedxml.common import DefusedXmlException
from PIL import Image
from pypdf import PdfReader

from server.ai import CompatibleAdapter, ExtractiveAdapter, validate_answer
from server.conversion import archive_guard, clean_html, extract, image_block, ingest, table_block
from server.exports import export_document
from server.models import WorkspaceConfig
from server.units import convert, normalize

EXAMPLES = Path(__file__).resolve().parents[2] / "examples"


@pytest.mark.parametrize(
    "value,source,target,expected",
    [
        ("1", "in", "mm", "25.4"),
        ("2.54", "cm", "in", "1"),
        ("1", "lb", "kg", "0.453592"),
        ("32", "F", "C", "0"),
        ("273.15", "K", "C", "0"),
        ("100", "C", "F", "212"),
        ("1", "bar", "kPa", "100"),
        ("1000", "Wh", "kWh", "1"),
        ("24000", "mV", "V", "24"),
        ("0", "m", "mm", "0"),
    ],
)
def test_units(value, source, target, expected):
    """Verify offsets, factors, zero and six-decimal display precision."""
    assert convert(value, source, target) == expected


@pytest.mark.parametrize(
    "value,source,target",
    [
        ("NaN", "in", "mm"),
        ("Infinity", "m", "mm"),
        ("-274", "C", "K"),
        ("1", "kg", "mm"),
        ("wat", "in", "mm"),
        ("1e99", "m", "mm"),
        ("1e-99", "m", "mm"),
        ("1", "unknown", "mm"),
    ],
)
def test_bad_units(value, source, target):
    """Reject nonfinite, nonsensical, incompatible and over-precision measurements."""
    with pytest.raises(ValueError):
        convert(value, source, target)


def test_provenance_and_ambiguity():
    """Only explicit bounded unit tokens convert; originals and offsets are retained."""
    text, records = normalize("Width 2 in, 3 cm; code MC-240; 50 percent; 10USD", {"length": "mm"})
    assert text == "Width 50.8 mm, 30 mm; code MC-240; 50 percent; 10USD"
    assert records[0]["original"] == "2 in"
    assert records[0]["source_start"] == 6
    assert normalize("There are 2 in stock", {"length": "mm"}) == ("There are 2 in stock", [])
    # Adversarial long whitespace must be scanned once, not regex-backtracked.
    spaced = "2 in" + " " * 150000 + "stock"
    assert normalize(spaced, {"length": "mm"}) == (spaced, [])
    assert normalize("2 in 3 cm", {"length": "mm"})[0] == "50.8 mm 30 mm"
    assert normalize("2 in\t ", {"length": "mm"})[0] == "50.8 mm\t "


@pytest.mark.parametrize(
    "settings",
    [
        {"units": {"length": "kg"}},
        {"sections": ["overview"]},
        {"sections": ["content", "content"]},
        {"data_columns": {"product": "x"}},
        {"extra": "code"},
    ],
)
def test_config_rejection(settings):
    """Configuration remains validated data, never an executable expression."""
    with pytest.raises(ValueError):
        WorkspaceConfig(title="Test", profile="industrial", **settings)


@pytest.mark.parametrize(
    "filename",
    [
        "industrial-sales.csv",
        "mixed-measurements.csv",
        "renewable-specifications.xlsx",
        "laboratory-record.json",
        "service-record.xml",
        "installation-note.md",
        "controller-performance.pdf",
        "commissioning-pack.docx",
        "throughput.png",
    ],
)
def test_fixtures(filename):
    """Run every realistic source through the same canonical HTML pipeline."""
    result = ingest(
        filename,
        (EXAMPLES / filename).read_bytes(),
        WorkspaceConfig(title="Test", profile="industrial"),
    )
    assert result["html"].startswith("<!doctype html>")
    assert result["blocks"]
    assert len(result["provenance"]["sha256"]) == 64
    if filename in {"controller-performance.pdf", "commissioning-pack.docx"}:
        assert any(block["kind"] == "figure" for block in result["blocks"])
        assert any(block["kind"] == "table" for block in result["blocks"])
        assert result["review_status"] == "needs-review"
    if filename == "commissioning-pack.docx":
        assert any(block["kind"] == "equation" for block in result["blocks"])


@pytest.mark.parametrize(
    "name,data",
    [
        (
            "test.html",
            b'<script>alert(1)</script><img src="https://evil.test/a"><a href="javascript:alert(1)">bad</a><p>2 in</p>',
        ),
        ("test.md", b"# Heading\n\n**2 in**"),
        ("test.tsv", b"part\twidth\nA\t2 in"),
        ("test.txt", b"2 in\n\n3 cm"),
        ("test.json", b'{"width":"2 in"}'),
    ],
)
def test_text_types(name, data):
    """Canonical text paths sanitize active content while preserving structure."""
    result = ingest(name, data, WorkspaceConfig(title="Test", profile="industrial"))
    assert "javascript:" not in result["html"] and "<script" not in result["html"]
    assert "50.8 mm" in result["html"]


@pytest.mark.parametrize(
    "name,data",
    [
        ("a.exe", b"abc"),
        ("a.txt", b""),
        ("a.txt", b"\x00"),
        ("a.txt", b"\xff"),
        ("a.json", b"NaN"),
        ("a.xml", b'<!DOCTYPE x [<!ENTITY evil SYSTEM "file:///etc/passwd">]><x>&evil;</x>'),
        ("a.pdf", b"wrong"),
        ("a.docx", b"wrong"),
    ],
)
def test_reject_bad_files(name, data):
    """Unknown, corrupt, malicious, binary-text and unsafe XML never silently succeed."""
    with pytest.raises((ValueError, UnicodeDecodeError, zipfile.BadZipFile, DefusedXmlException)):
        extract(name, data)


def test_zip_and_table_limits():
    """Expanded Office archives and table shapes have bounded work budgets."""
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("word/document.xml", "x" * 100000)
    with pytest.raises(ValueError):
        archive_guard(output.getvalue(), "word/document.xml")
    with pytest.raises(ValueError):
        table_block([[1] * 41])
    assert "<script" not in clean_html("<p>Safe</p><script>bad</script>")


@pytest.mark.parametrize("format_name", ["html", "json", "md", "csv", "docx", "pdf"])
def test_exports(format_name):
    """All export formats derive from HTML and produce readable artifacts."""
    result = ingest(
        "table.csv",
        b"part,width\nA,2 in\n=HYPERLINK(1),3 cm",
        WorkspaceConfig(title="Test", profile="industrial"),
    )
    payload = export_document(result, format_name)
    assert payload
    if format_name == "pdf":
        assert "50.8 mm" in PdfReader(io.BytesIO(payload)).pages[0].extract_text()
    if format_name == "docx":
        assert zipfile.is_zipfile(io.BytesIO(payload))
    if format_name == "csv":
        assert "'=HYPERLINK" in payload.decode("utf-8-sig")
    if format_name == "json":
        assert json.loads(payload)["provenance"]["export_path"] == ["html", "json"]


def test_rich_exports():
    """Figures and tables survive simplified PDF and DOCX export paths."""
    result = ingest(
        "pack.docx",
        (EXAMPLES / "commissioning-pack.docx").read_bytes(),
        WorkspaceConfig(title="Test", profile="industrial"),
    )
    assert export_document(result, "pdf").startswith(b"%PDF")
    assert export_document(result, "docx").startswith(b"PK")
    with pytest.raises(ValueError):
        export_document(result, "exe")


def test_ai_contracts():
    """Grounded extraction is honest about vision; fabricated citations are rejected."""
    context = [{"id": "public-1", "text": "Controller width is 100 mm"}]
    adapter = ExtractiveAdapter()
    answer = validate_answer(adapter.answer("controller width", context), context)
    assert answer["citations"] == ["public-1"]
    assert "cannot interpret" in adapter.answer("figure", context, "image")["answer"]
    for result in [
        {"answer": "test", "citations": ["private-2"]},
        {"answer": 2, "citations": []},
        {"answer": "x", "citations": "x"},
    ]:
        with pytest.raises(ValueError):
            validate_answer(result, context)
    for endpoint in [
        "http://external.test/api",
        "file:///etc/passwd",
        "https://user:password@api.test/chat",
        "https://api.test/chat?key=x",
    ]:
        with pytest.raises(ValueError):
            CompatibleAdapter(endpoint, "test")
    assert CompatibleAdapter("http://127.0.0.1:11434/v1/chat/completions", "local").model == "local"


def test_large_image():
    """Reject oversized images before conversion to a full in-memory raster."""
    output = io.BytesIO()
    Image.new("RGB", (3000, 3000)).save(output, "PNG")
    with pytest.raises(ValueError):
        image_block(output.getvalue(), "huge")
