# @index-begin
# @symbol variable/parameter: FORMATS L63
# @symbol function/class: export_document L73
# @symbol variable/parameter: format_name L73
# @symbol variable/parameter: result L73
# @symbol variable/parameter: html L75
# @symbol variable/parameter: standard L76
# @symbol variable/parameter: soup L79
# @symbol variable/parameter: body L80
# @symbol variable/parameter: parts L90
# @symbol variable/parameter: node L91
# @symbol variable/parameter: prefix L92
# @symbol variable/parameter: tables L102
# @symbol variable/parameter: output L105
# @symbol variable/parameter: writer L106
# @symbol variable/parameter: table L107
# @symbol variable/parameter: row L108
# @symbol variable/parameter: cell L109
# @symbol variable/parameter: cells L109
# @symbol variable/parameter: document L121
# @symbol variable/parameter: section L122
# @symbol variable/parameter: height L123
# @symbol variable/parameter: width L123
# @symbol variable/parameter: font L127
# @symbol variable/parameter: name L130
# @symbol variable/parameter: text L136
# @symbol variable/parameter: rows L138
# @symbol variable/parameter: columns L139
# @symbol variable/parameter: index L143
# @symbol variable/parameter: column L144
# @symbol variable/parameter: styles L159
# @symbol variable/parameter: fonts L160
# @symbol variable/parameter: bold L165
# @symbol variable/parameter: normal L165
# @symbol variable/parameter: heading L169
# @symbol variable/parameter: page L172
# @symbol variable/parameter: available L175
# @symbol variable/parameter: flow L176
# @symbol variable/parameter: padded L191
# @symbol variable/parameter: start L192
# @symbol variable/parameter: graphic L209
# @symbol variable/parameter: ratio L210
# @symbol variable/parameter: style L220
# @index-end
"""HTML-first export adapters with predictable, simplified document layout. Index: docs/code-index.md."""

import base64
import csv
import io
import json
from html import escape

from bs4 import BeautifulSoup
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape, letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .models import OutputStandard

FORMATS = {
    "html": "text/html",
    "json": "application/json",
    "md": "text/markdown",
    "csv": "text/csv",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "pdf": "application/pdf",
}


def export_document(result: dict, format_name: str) -> bytes:
    """Derive every representation from existing canonical HTML; structured JSON also carries provenance."""
    html = result["html"]
    standard = OutputStandard.model_validate(result.get("standard", {}).get("output_standard", {}))
    if standard.enforce_export and format_name != standard.default_export:
        raise ValueError("This document standard restricts exports to " + standard.default_export)
    soup = BeautifulSoup(html, "html.parser")
    body = soup.body
    if format_name == "html":
        return html.encode()
    if format_name == "json":
        return json.dumps(
            {**result, "provenance": {**result["provenance"], "export_path": ["html", "json"]}},
            ensure_ascii=False,
            indent=2,
        ).encode()
    if format_name == "md":
        parts = []
        for node in body.find_all(["h1", "h2", "h3", "p", "pre", "li", "tr", "figcaption"]):
            prefix = (
                "#" * int(node.name[1]) + " "
                if node.name.startswith("h")
                else "- "
                if node.name == "li"
                else ""
            )
            parts.append(prefix + node.get_text(" ", strip=True))
        return "\n\n".join(parts).encode()
    if format_name == "csv":
        tables = [table for table in body.find_all("table") if table.find("tr")]
        if not tables:
            raise ValueError("No tabular content for CSV; choose HTML, JSON, Markdown, DOCX or PDF")
        output = io.StringIO(newline="")
        writer = csv.writer(output)
        for table in tables:
            for row in table.find_all("tr"):
                cells = [cell.get_text(" ", strip=True) for cell in row.find_all(["th", "td"])]
                # Spreadsheet formula injection protection on exported untrusted cells.
                writer.writerow(
                    [
                        "'" + cell
                        if cell.lstrip().startswith(("=", "+", "-", "@", "\t", "\r"))
                        else cell
                        for cell in cells
                    ]
                )
        return output.getvalue().encode("utf-8-sig")
    if format_name == "docx":
        document = Document()
        section = document.sections[0]
        width, height = (595.2756, 841.8898) if standard.paper == "A4" else (612, 792)
        if standard.orientation == "landscape":
            width, height = height, width
        section.page_width, section.page_height = Pt(width), Pt(height)
        font = {"sans": "Arial", "serif": "Times New Roman", "mono": "Courier New"}[standard.font]
        document.styles["Normal"].font.name = font
        document.styles["Normal"].font.size = Pt(standard.font_size)
        for name in ["Heading 1", "Heading 2", "Heading 3"]:
            document.styles[name].font.name = font
            document.styles[name].font.color.rgb = RGBColor.from_string(standard.accent[1:])
        for node in body.find_all(["h1", "h2", "h3", "p", "pre", "table", "img", "figcaption"]):
            if node.find_parent("table"):
                continue
            text = node.get_text(" ", strip=True)
            if node.name == "table":
                rows = node.find_all("tr")
                columns = max((len(row.find_all(["td", "th"])) for row in rows), default=0)
                if columns:
                    table = document.add_table(rows=len(rows), cols=columns)
                    table.style = "Table Grid"
                    for index, row in enumerate(rows):
                        for column, cell in enumerate(row.find_all(["td", "th"])):
                            table.cell(index, column).text = cell.get_text(" ", strip=True)
            elif node.name == "img":
                document.add_picture(
                    io.BytesIO(base64.b64decode(node["src"].split(",", 1)[1])), width=Inches(5)
                )
            elif node.name.startswith("h"):
                document.add_heading(text, int(node.name[1]))
            else:
                document.add_paragraph(text)
        output = io.BytesIO()
        document.save(output)
        return output.getvalue()
    if format_name == "pdf":
        output = io.BytesIO()
        styles = getSampleStyleSheet()
        fonts = {
            "sans": ("Helvetica", "Helvetica-Bold"),
            "serif": ("Times-Roman", "Times-Bold"),
            "mono": ("Courier", "Courier-Bold"),
        }
        normal, bold = fonts[standard.font]
        styles["BodyText"].fontName = normal
        styles["BodyText"].fontSize = standard.font_size
        styles["BodyText"].leading = standard.font_size * 1.4
        for heading in ["Heading1", "Heading2", "Heading3"]:
            styles[heading].fontName = bold
            styles[heading].textColor = colors.HexColor(standard.accent)
        page = A4 if standard.paper == "A4" else letter
        if standard.orientation == "landscape":
            page = landscape(page)
        available = page[0] - 120
        flow = []
        for node in body.find_all(["h1", "h2", "h3", "p", "pre", "table", "img", "figcaption"]):
            if node.find_parent("table"):
                continue
            if node.name == "table":
                rows = [
                    [
                        Paragraph(escape(cell.get_text(" ", strip=True)), styles["BodyText"])
                        for cell in row.find_all(["td", "th"])
                    ]
                    for row in node.find_all("tr")
                ]
                if rows:
                    # Wide tables are split into groups to keep text visible on a Letter page.
                    columns = max(map(len, rows))
                    padded = [row + [""] * (columns - len(row)) for row in rows]
                    for start in range(0, columns, 5):
                        table = Table(
                            [row[start : start + 5] for row in padded],
                            repeatRows=1,
                            colWidths=[available / min(5, columns - start)]
                            * min(5, columns - start),
                        )
                        table.setStyle(
                            TableStyle(
                                [
                                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                ]
                            )
                        )
                        flow.extend([table, Spacer(1, 12)])
            elif node.name == "img":
                graphic = Image(io.BytesIO(base64.b64decode(node["src"].split(",", 1)[1])))
                ratio = min(
                    available / graphic.imageWidth, (page[1] - 120) / graphic.imageHeight, 1
                )
                graphic.drawWidth, graphic.drawHeight = (
                    graphic.imageWidth * ratio,
                    graphic.imageHeight * ratio,
                )
                flow.append(graphic)
            else:
                text = escape(node.get_text(" ", strip=True)).replace("\n", "<br/>")
                style = (
                    styles["Heading" + node.name[1]]
                    if node.name in {"h1", "h2", "h3"}
                    else styles["BodyText"]
                )
                flow.extend([Paragraph(text, style), Spacer(1, 8)])
        SimpleDocTemplate(output, pagesize=page, rightMargin=60, leftMargin=60).build(flow)
        return output.getvalue()
    raise ValueError("Unknown export format")
