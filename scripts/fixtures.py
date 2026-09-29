# @index-begin
# @symbol variable/parameter: ROOT L37
# @symbol function/class: main L40
# @symbol variable/parameter: folder L42
# @symbol variable/parameter: raster L44
# @symbol variable/parameter: draw L45
# @symbol variable/parameter: index L47
# @symbol variable/parameter: label L47
# @symbol variable/parameter: value L47
# @symbol variable/parameter: x L48
# @symbol variable/parameter: size L52
# @symbol variable/parameter: icon L53
# @symbol variable/parameter: pen L54
# @symbol variable/parameter: rows L67
# @symbol variable/parameter: output L73
# @symbol variable/parameter: workbook L79
# @symbol variable/parameter: sheet L80
# @symbol variable/parameter: row L82
# @symbol variable/parameter: styles L111
# @symbol variable/parameter: table L112
# @symbol variable/parameter: flow L129
# @index-end
"""Generate deterministic synthetic sources and PWA raster icons. Index: docs/code-index.md."""

import csv
import io
import json
from pathlib import Path

from openpyxl import Workbook
from PIL import Image, ImageDraw
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image as PDFImage
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parent.parent


def main():
    """Create small cross-format examples; embedded chart values match accompanying table rows."""
    folder = ROOT / "examples"
    folder.mkdir(exist_ok=True)
    raster = Image.new("RGB", (640, 300), "#f5f6f2")
    draw = ImageDraw.Draw(raster)
    draw.text((25, 20), "Synthetic controller throughput (messages/second)", fill="#173c33")
    for index, (label, value) in enumerate([("A", 120), ("B", 180), ("C", 240)]):
        x = 100 + index * 170
        draw.rectangle((x, 260 - value * 0.75, x + 75, 260), fill="#749858")
        draw.text((x, 275), f"{label}: {value}", fill="#173c33")
    raster.save(folder / "throughput.png")
    for size in [192, 512]:
        icon = Image.new("RGB", (size, size), "#163e35")
        pen = ImageDraw.Draw(icon)
        pen.line(
            [
                (size * 0.18, size * 0.28),
                (size * 0.32, size * 0.72),
                (size * 0.5, size * 0.39),
                (size * 0.68, size * 0.72),
                (size * 0.82, size * 0.28),
            ],
            fill="#d5e8b9",
            width=int(size * 0.07),
        )
        icon.save(ROOT / "public" / f"icon-{size}.png")
    rows = [
        ["product", "customer", "month", "quantity", "revenue_cents"],
        ["MC-240", "north", "2026-01", 32, 2396800],
        ["IO-16", "north", "2026-01", 45, 1300500],
        ["PS-24", "south", "2026-01", 60, 534000],
    ]
    output = io.StringIO(newline="")
    csv.writer(output).writerows(rows)
    (folder / "industrial-sales.csv").write_text(output.getvalue(), encoding="utf-8")
    (folder / "mixed-measurements.csv").write_text(
        "component,width,mass\nCabinet,4.25 in,2.5 lb\nBracket,8.2 cm,450 g\n", encoding="utf-8"
    )
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Synthetic specifications"
    for row in [
        ["product", "width", "temperature", "mass"],
        ["SE-410", "113.4 cm", "104 F", "48.5 lb"],
        ["BAT-5", "22 in", "45 C", "52 kg"],
    ]:
        sheet.append(row)
    workbook.save(folder / "renewable-specifications.xlsx")
    (folder / "laboratory-record.json").write_text(
        json.dumps(
            [
                {
                    "product": "AT-220",
                    "width": "22 cm",
                    "mass": "3.5 kg",
                    "status": "Synthetic calibration passed",
                }
            ],
            indent=2,
        ),
        encoding="utf-8",
    )
    (folder / "service-record.xml").write_text(
        "<record><product>MC-240</product><width>4.25 in</width><status>Synthetic inspection passed</status></record>",
        encoding="utf-8",
    )
    (folder / "installation-note.md").write_text(
        "# Synthetic installation note\n\nCabinet clearance: **2 in**. Preserve source revision and review warnings.\n\nNo real-world installation approval is implied.\n",
        encoding="utf-8",
    )
    styles = getSampleStyleSheet()
    table = Table(
        [
            ["Variant", "Throughput", "Width"],
            ["A", "120 messages/s", "4.25 in"],
            ["B", "180 messages/s", "8.2 cm"],
            ["C", "240 messages/s", "110 mm"],
        ],
        colWidths=[120, 180, 160],
    )
    table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.6, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eaf0e2")),
            ]
        )
    )
    flow = [
        Paragraph("Synthetic controller performance brief", styles["Title"]),
        Spacer(1, 18),
        Paragraph(
            "Meridian Controls reference scenario. These invented figures demonstrate extraction and are not hardware guarantees.",
            styles["BodyText"],
        ),
        Spacer(1, 18),
        table,
        Spacer(1, 18),
        PDFImage(str(folder / "throughput.png"), width=460, height=215),
        Spacer(1, 18),
        Paragraph(
            "Equation: throughput = processed messages / elapsed seconds. Scaled value = raw / 65535 * 10 V.",
            styles["BodyText"],
        ),
    ]
    SimpleDocTemplate(
        str(folder / "controller-performance.pdf"),
        pagesize=(612, 792),
        leftMargin=60,
        rightMargin=60,
    ).build(flow)
    print("Generated synthetic source fixtures and PWA icons")


if __name__ == "__main__":
    main()
