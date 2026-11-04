/* @index-begin
 * @symbol function/class: main L30
 * @symbol variable/parameter: cases L31
 * @symbol variable/parameter: scenario L35
 * @symbol variable/parameter: count L36
 * @symbol variable/parameter: widths L37
 * @symbol variable/parameter: _ L39
 * @symbol variable/parameter: index L39
 * @symbol variable/parameter: document L42
 * @symbol variable/parameter: row L58
 * @symbol variable/parameter: value L61
@index-end */
/** Jason Stys: reproducible fictional industry DOCX sources, not customer records.
 * Functions/variables and exact lines: docs/code-index.md.
 * Uses explicit Letter page geometry and matching table/cell widths. Generated
 * binaries and the JSON source cases are reviewed in Git for Python-only CI.
 */
import { readFile, mkdir, writeFile } from "node:fs/promises";
import {
  Document,
  Packer,
  Paragraph,
  Table,
  TableRow,
  TableCell,
  WidthType,
} from "docx";

/** Produce valid, bounded Word fixtures independently of the Python export path. */
async function main() {
  const cases = JSON.parse(
    await readFile("examples/industry-cases.json", "utf8"),
  );
  await mkdir("examples/industry-inputs", { recursive: true });
  for (const scenario of cases) {
    const count = scenario.headers.length;
    const widths = Array.from(
      { length: count },
      (_, index) =>
        Math.floor(9360 / count) + (index === count - 1 ? 9360 % count : 0),
    );
    const document = new Document({
      creator: "Jason Stys",
      sections: [
        {
          properties: {
            page: {
              size: { width: 12240, height: 15840 },
              margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
            },
          },
          children: [
            new Paragraph(scenario.company + " - synthetic training fixture"),
            new Table({
              width: { size: 9360, type: WidthType.DXA },
              columnWidths: widths,
              rows: [scenario.headers, ...scenario.rows].map(
                (row) =>
                  new TableRow({
                    children: row.map(
                      (value, index) =>
                        new TableCell({
                          width: { size: widths[index], type: WidthType.DXA },
                          margins: {
                            top: 80,
                            bottom: 80,
                            left: 100,
                            right: 100,
                          },
                          children: [new Paragraph(value)],
                        }),
                    ),
                  }),
              ),
            }),
          ],
        },
      ],
    });
    await writeFile(
      `examples/industry-inputs/${scenario.profile}.docx`,
      await Packer.toBuffer(document),
    );
  }
}
await main();
