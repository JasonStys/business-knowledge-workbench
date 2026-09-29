/* @index-begin
 * @symbol variable/parameter: rows L24
 * @symbol variable/parameter: table L29
 * @symbol variable/parameter: row L33
 * @symbol variable/parameter: value L36
 * @symbol variable/parameter: document L46
@index-end */
/** Synthetic DOCX with a table, figure and Office Math equation. Index: docs/code-index.md. */
import {
  Document,
  Packer,
  Paragraph,
  TextRun,
  Table,
  TableRow,
  TableCell,
  ImageRun,
  HeadingLevel,
  WidthType,
  Math as OfficeMath,
  MathRun,
} from "docx";
import { readFile, writeFile } from "node:fs/promises";
const rows = [
  ["Product", "Width", "Input"],
  ["MC-240", "4.25 in", "24 V"],
  ["IO-16", "8.2 cm", "24000 mV"],
];
const table = new Table({
  width: { size: 9360, type: WidthType.DXA },
  columnWidths: [3120, 3120, 3120],
  rows: rows.map(
    (row) =>
      new TableRow({
        children: row.map(
          (value) =>
            new TableCell({
              width: { size: 3120, type: WidthType.DXA },
              margins: { top: 80, bottom: 80, left: 120, right: 120 },
              children: [new Paragraph({ children: [new TextRun(value)] })],
            }),
        ),
      }),
  ),
});
const document = new Document({
  styles: { default: { document: { run: { font: "Arial", size: 22 } } } },
  sections: [
    {
      properties: {
        page: {
          size: { width: 12240, height: 15840 },
          margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
        },
      },
      children: [
        new Paragraph({
          text: "Synthetic controller commissioning pack",
          heading: HeadingLevel.HEADING_1,
        }),
        new Paragraph(
          "Invented source material for extraction testing. No real installation instructions or performance guarantees.",
        ),
        table,
        new Paragraph({
          children: [
            new ImageRun({
              type: "png",
              data: await readFile("examples/throughput.png"),
              transformation: { width: 460, height: 216 },
              altText: {
                name: "Synthetic throughput chart",
                title: "Throughput comparison",
                description:
                  "Variants A, B, C: 120, 180, 240 messages per second",
              },
            }),
          ],
        }),
        new Paragraph({
          children: [
            new OfficeMath({ children: [new MathRun("V = raw / 65535 × 10")] }),
          ],
        }),
      ],
    },
  ],
});
await writeFile(
  "examples/commissioning-pack.docx",
  await Packer.toBuffer(document),
);
