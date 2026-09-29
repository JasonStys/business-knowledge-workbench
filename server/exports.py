# @index-begin
# @symbol variable/parameter: FORMATS L48
# @symbol function/class: export_document L58
# @symbol variable/parameter: format_name L58
# @symbol variable/parameter: result L58
# @symbol variable/parameter: html L60
# @symbol variable/parameter: soup L61
# @symbol variable/parameter: body L62
# @symbol variable/parameter: parts L72
# @symbol variable/parameter: node L73
# @symbol variable/parameter: prefix L74
# @symbol variable/parameter: output L84
# @symbol variable/parameter: writer L85
# @symbol variable/parameter: table L86
# @symbol variable/parameter: row L87
# @symbol variable/parameter: cell L88
# @symbol variable/parameter: cells L88
# @symbol variable/parameter: document L100
# @symbol variable/parameter: section L101
# @symbol variable/parameter: text L106
# @symbol variable/parameter: rows L108
# @symbol variable/parameter: columns L109
# @symbol variable/parameter: index L113
# @symbol variable/parameter: column L114
# @symbol variable/parameter: styles L129
# @symbol variable/parameter: flow L130
# @symbol variable/parameter: padded L145
# @symbol variable/parameter: start L146
# @symbol variable/parameter: graphic L162
# @symbol variable/parameter: ratio L163
# @symbol variable/parameter: style L171
# @index-end
"""HTML-first export adapters with predictable, simplified document layout. Index: docs/code-index.md."""

import base64
import csv
import io
import json
from html import escape

from bs4 import BeautifulSoup
from docx import Document
from docx.shared import Inches
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

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
        output = io.StringIO(newline="")
        writer = csv.writer(output)
        for table in body.find_all("table"):
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
        section.page_width, section.page_height = Inches(8.5), Inches(11)
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
                            colWidths=[480 / min(5, columns - start)] * min(5, columns - start),
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
                ratio = min(480 / graphic.imageWidth, 350 / graphic.imageHeight, 1)
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
        SimpleDocTemplate(output, pagesize=(612, 792), rightMargin=60, leftMargin=60).build(flow)
        return output.getvalue()
    raise ValueError("Unknown export format")
