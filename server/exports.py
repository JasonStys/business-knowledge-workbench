# @index-begin
# @symbol variable/parameter: FORMATS L79
# @symbol function/class: export_document L89
# @symbol variable/parameter: format_name L89
# @symbol variable/parameter: result L89
# @symbol variable/parameter: html L91
# @symbol variable/parameter: standard L92
# @symbol variable/parameter: soup L95
# @symbol variable/parameter: body L96
# @symbol variable/parameter: parts L106
# @symbol variable/parameter: node L107
# @symbol variable/parameter: prefix L108
# @symbol variable/parameter: tables L118
# @symbol variable/parameter: output L121
# @symbol variable/parameter: writer L122
# @symbol variable/parameter: table L123
# @symbol variable/parameter: row L124
# @symbol variable/parameter: cell L125
# @symbol variable/parameter: cells L125
# @symbol variable/parameter: document L137
# @symbol variable/parameter: zoom L140
# @symbol variable/parameter: section L143
# @symbol variable/parameter: height L144
# @symbol variable/parameter: width L144
# @symbol variable/parameter: name L154
# @symbol variable/parameter: footer L159
# @symbol variable/parameter: number L163
# @symbol variable/parameter: font L166
# @symbol variable/parameter: paragraph L169
# @symbol variable/parameter: text L188
# @symbol variable/parameter: rows L190
# @symbol variable/parameter: columns L191
# @symbol variable/parameter: column_width L203
# @symbol variable/parameter: column L208
# @symbol variable/parameter: index L210
# @symbol variable/parameter: styles L233
# @symbol variable/parameter: fonts L234
# @symbol variable/parameter: bold L239
# @symbol variable/parameter: normal L239
# @symbol variable/parameter: heading L246
# @symbol variable/parameter: page L249
# @symbol variable/parameter: margin L252
# @symbol variable/parameter: available L253
# @symbol variable/parameter: flow L254
# @symbol variable/parameter: padded L273
# @symbol variable/parameter: start L274
# @symbol variable/parameter: graphic L291
# @symbol variable/parameter: ratio L292
# @symbol variable/parameter: style L304
# @symbol variable/parameter: canvas L311
# @symbol function/class: decorate L311
# @symbol variable/parameter: furniture L314
# @symbol variable/parameter: top L316
# @symbol variable/parameter: item L317
# @symbol variable/parameter: _ L318
# @index-end
"""HTML-first export adapters with predictable, simplified document layout. Index: docs/code-index.md."""

import base64
import csv
import io
import json
from html import escape

from bs4 import BeautifulSoup
from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Mm, Pt, RGBColor
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
        # python-docx's stock template leaves this required OOXML attribute
        # unspecified. Emit schema-valid settings for strict document readers.
        zoom = document.settings.element.find(qn("w:zoom"))
        if zoom is not None:
            zoom.set(qn("w:percent"), "100")
        section = document.sections[0]
        width, height = (595.2756, 841.8898) if standard.paper == "A4" else (612, 792)
        if standard.orientation == "landscape":
            width, height = height, width
        section.page_width, section.page_height = Pt(width), Pt(height)
        section.orientation = (
            WD_ORIENT.LANDSCAPE if standard.orientation == "landscape" else WD_ORIENT.PORTRAIT
        )
        section.top_margin = section.bottom_margin = Mm(standard.margin_mm)
        section.left_margin = section.right_margin = Mm(standard.margin_mm)
        section.header_distance = section.footer_distance = Mm(2)
        for name in ("Header", "Footer"):
            document.styles[name].font.size = Pt(8)
            document.styles[name].paragraph_format.space_after = Pt(0)
            document.styles[name].paragraph_format.line_spacing = 1.0
        section.header.paragraphs[0].text = standard.header_text
        footer = section.footer.paragraphs[0]
        footer.text = standard.footer_text
        if standard.page_numbers:
            footer.add_run("  Page ")
            number = OxmlElement("w:fldSimple")
            number.set(qn("w:instr"), "PAGE")
            footer._p.append(number)
        font = {"sans": "Arial", "serif": "Times New Roman", "mono": "Courier New"}[standard.font]
        document.styles["Normal"].font.name = font
        document.styles["Normal"].font.size = Pt(standard.font_size)
        paragraph = document.styles["Normal"].paragraph_format
        paragraph.line_spacing = standard.line_spacing
        paragraph.space_after = Pt(standard.paragraph_after_pt)
        paragraph.alignment = {
            "left": WD_ALIGN_PARAGRAPH.LEFT,
            "center": WD_ALIGN_PARAGRAPH.CENTER,
            "right": WD_ALIGN_PARAGRAPH.RIGHT,
            "justify": WD_ALIGN_PARAGRAPH.JUSTIFY,
        }[standard.alignment]
        for name in ["Heading 1", "Heading 2", "Heading 3"]:
            document.styles[name].font.name = font
            document.styles[name].font.color.rgb = RGBColor.from_string(standard.accent[1:])
        for node in body.find_all(
            ["h1", "h2", "h3", "p", "pre", "li", "table", "img", "figcaption"]
        ):
            if node.find_parent(["header", "footer"]) or "page-note" in node.get("class", []):
                continue
            if node.find_parent("table"):
                continue
            text = node.get_text(" ", strip=True)
            if node.name == "table":
                rows = node.find_all("tr")
                columns = max((len(row.find_all(["td", "th"])) for row in rows), default=0)
                if columns:
                    table = document.add_table(rows=len(rows), cols=columns)
                    table.style = "Table Grid"
                    table.autofit = False
                    available = (
                        int(section.page_width)
                        - int(section.left_margin)
                        - int(section.right_margin)
                    )
                    table._tbl.tblPr.find(qn("w:tblW")).set(qn("w:w"), str(round(available / 635)))
                    table._tbl.tblPr.find(qn("w:tblW")).set(qn("w:type"), "dxa")
                    column_width = (
                        int(section.page_width)
                        - int(section.left_margin)
                        - int(section.right_margin)
                    ) // columns
                    for column in table.columns:
                        column.width = column_width
                    for index, row in enumerate(rows):
                        for column, cell in enumerate(row.find_all(["td", "th"])):
                            table.cell(index, column).text = cell.get_text(" ", strip=True)
                            table.cell(index, column).width = column_width
            elif node.name == "img":
                document.add_picture(
                    io.BytesIO(base64.b64decode(node["src"].split(",", 1)[1])),
                    width=min(
                        Inches(5),
                        int(section.page_width)
                        - int(section.left_margin)
                        - int(section.right_margin),
                    ),
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
        styles["BodyText"].leading = standard.font_size * standard.line_spacing
        styles["BodyText"].alignment = {"left": 0, "center": 1, "right": 2, "justify": 4}[
            standard.alignment
        ]
        for heading in ["Heading1", "Heading2", "Heading3"]:
            styles[heading].fontName = bold
            styles[heading].textColor = colors.HexColor(standard.accent)
        page = A4 if standard.paper == "A4" else letter
        if standard.orientation == "landscape":
            page = landscape(page)
        margin = standard.margin_mm * 72 / 25.4
        available = page[0] - 2 * margin
        flow = []
        for node in body.find_all(
            ["h1", "h2", "h3", "p", "pre", "li", "table", "img", "figcaption"]
        ):
            if node.find_parent(["header", "footer"]) or "page-note" in node.get("class", []):
                continue
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
                    available / graphic.imageWidth, (page[1] - 2 * margin) / graphic.imageHeight, 1
                )
                graphic.drawWidth, graphic.drawHeight = (
                    graphic.imageWidth * ratio,
                    graphic.imageHeight * ratio,
                )
                flow.append(graphic)
            else:
                text = (
                    escape(node.get_text(" ", strip=True)).replace("→", "->").replace("\n", "<br/>")
                )
                style = (
                    styles["Heading" + node.name[1]]
                    if node.name in {"h1", "h2", "h3"}
                    else styles["BodyText"]
                )
                flow.extend([Paragraph(text, style), Spacer(1, standard.paragraph_after_pt)])

        def decorate(canvas, document):
            """Draw bounded plain-text running furniture; never interpret markup or paths."""
            canvas.saveState()
            furniture = styles["BodyText"].clone("Furniture")
            furniture.fontSize, furniture.leading, furniture.alignment = 8, 9, 0
            for text, top in ((standard.header_text, True), (standard.footer_text, False)):
                item = Paragraph(escape(text), furniture)
                _, height = item.wrap(
                    available - (70 if standard.page_numbers and not top else 0), margin
                )
                item.drawOn(canvas, margin, page[1] - margin + 3 if top else margin - 3 - height)
            canvas.setFont(normal, 8)
            if standard.page_numbers:
                canvas.drawRightString(page[0] - margin, margin - 12, "Page " + str(document.page))
            canvas.restoreState()

        SimpleDocTemplate(
            output,
            pagesize=page,
            rightMargin=margin,
            leftMargin=margin,
            topMargin=margin,
            bottomMargin=margin,
        ).build(flow, onFirstPage=decorate, onLaterPages=decorate)
        return output.getvalue()
    raise ValueError("Unknown export format")
