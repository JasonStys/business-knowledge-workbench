/* @index-begin
 * @symbol function/class: escape L27
 * @symbol variable/parameter: value L27
 * @symbol variable/parameter: c L30
 * @symbol variable/parameter: config L38
 * @symbol function/class: standardFields L38
 * @symbol variable/parameter: standard L39
 * @symbol variable/parameter: select L40
 * @symbol variable/parameter: label L41
 * @symbol variable/parameter: name L42
 * @symbol variable/parameter: values L43
 * @symbol variable/parameter: current L44
 * @symbol variable/parameter: [key, label] L70
 * @symbol variable/parameter: data L88
 * @symbol function/class: readStandard L88
 * @symbol variable/parameter: key L93
 * @symbol function/class: measurementExample L127
 * @symbol variable/parameter: raw L128
@index-end */
/** Jason Stys: finite document-layout controls and safe standard-field drafts.
 * Functions/variables and exact line locations: docs/code-index.md.
 * Authoritative validation and publication permissions are enforced on the server.
 */
import type { Config, OutputStandard } from "./types";

/** Escape saved labels; no user HTML, CSS or expressions become executable code. */
function escape(value: unknown): string {
  return String(value ?? "").replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        c
      ]!,
  );
}

/** Render document-style controls without pretending to be a full Word layout engine. */
export function standardFields(config: Config): string {
  const standard = config.output_standard;
  const select = (
    label: string,
    name: string,
    values: string[],
    current: string,
  ): string =>
    `<label>${label}<select name="std-${name}">${values.map((value) => `<option value="${value}" ${value === current ? "selected" : ""}>${value}</option>`).join("")}</select></label>`;
  return `<fieldset><legend>Documentation and data output standard</legend>
  <p>Only the unlocked owner or database-authenticated legacy administrator may publish standards. These are draft controls, not permissions or executable templates.</p>
  <label>Standard name<input name="std-name" value="${escape(standard.name)}" minlength="2" maxlength="80" required></label>
  <div class="config-units">
  ${select("Standard export type", "default_export", ["html", "json", "md", "csv", "docx", "pdf"], standard.default_export)}
  ${select("Paper size", "paper", ["Letter", "A4"], standard.paper)}
  ${select("Page orientation", "orientation", ["portrait", "landscape"], standard.orientation)}
  ${select("Font family", "font", ["sans", "serif", "mono"], standard.font)}
  <label>Body font size (pt)<input name="std-font_size" type="number" min="10" max="16" value="${standard.font_size}" required></label>
  <label>Heading color<input name="std-accent" type="color" value="${escape(standard.accent)}"></label>
  <label>Page margins (mm)<input name="std-margin_mm" type="number" min="10" max="40" value="${standard.margin_mm}" required></label>
  ${select("Paragraph alignment", "alignment", ["left", "center", "right", "justify"], standard.alignment)}
  ${select("Line spacing", "line_spacing", ["1", "1.15", "1.5", "2"], String(standard.line_spacing))}
  <label>Paragraph spacing after (pt)<input name="std-paragraph_after_pt" type="number" min="0" max="24" value="${standard.paragraph_after_pt}" required></label>
  <label>Running header<input name="std-header_text" value="${escape(standard.header_text)}" maxlength="120"></label>
  <label>Running footer<input name="std-footer_text" value="${escape(standard.footer_text)}" maxlength="120"></label></div>
  <label class="check"><input name="std-page_numbers" type="checkbox" ${standard.page_numbers ? "checked" : ""}>Include page numbers in DOCX and PDF</label>
  <label class="check"><input name="std-enforce_export" type="checkbox" ${standard.enforce_export ? "checked" : ""}>Restrict document/report exports to the standard file type</label>
  <p>HTML is always generated first. Layout controls apply to HTML, DOCX and PDF; text/data exports preserve content rather than pagination. HTML preview shows header/footer once; DOCX/PDF use running furniture.</p>
  <h3>Section headings</h3><div class="config-units">${Object.entries(
    standard.section_titles,
  )
    .map(
      ([key, label]) =>
        `<label>${escape(key)} heading<input name="std-label-${key}" value="${escape(label)}" maxlength="80" required></label>`,
    )
    .join("")}</div>
  <h3>Table schema and field order</h3>
  <p>Add, reorder, remove or exclude fields. Exclusion reduces output clutter, not confidentiality: original evidence and source blocks are retained. Removing a field makes it an unknown column; choose Omit below to exclude unknown columns too. Enable at least one schema field, or clear all fields to preserve original tables.</p>
  <div id="standard-field-editor"></div><button type="button" id="standard-add-field" class="quiet">Add standard field</button>
  <button type="button" id="standard-example" class="quiet">Use measurement-table example</button>
  <details><summary>Advanced field definitions (JSON)</summary><label>Table columns (JSON)<textarea name="std-columns" rows="8" spellcheck="false">${escape(JSON.stringify(standard.columns, null, 2))}</textarea></label></details>
  <div class="config-units">${select("Extra table columns", "extra_columns", ["preserve", "reject", "omit"], standard.extra_columns)}${select("Tables covered by schema", "table_scope", ["matching", "all"], standard.table_scope)}</div>
  <p>Declare a source unit for bare numeric measurements; other values need explicit units. Select Keep source units for unused measurement types above. Matching applies only to recognized tables; All enforces every table.</p>
  <label>CSV sample for draft preview<textarea name="std-sample" rows="4" maxlength="16000">Component,Width\nPanel,4.25 in\nBracket,8.2 cm</textarea></label>
  <label>Optional file for draft preview<input id="standard-preview-file" type="file" accept=".txt,.md,.html,.htm,.csv,.tsv,.json,.xml,.docx,.xlsx,.pdf,.png,.jpg,.jpeg,.webp"></label>
  <p>With a file selected, its actual content replaces the CSV sample in this preview. Up to 4 MiB; preview never inserts a database record or sends content to AI.</p>
  <button type="button" id="standard-preview" class="quiet">Preview draft standard</button><p id="standard-preview-status" role="status"></p><iframe id="standard-preview-frame" title="Draft standard preview" sandbox="" hidden></iframe></fieldset>`;
}

/** Read bounded values from the form; raw schema remains server-validated data. */
export function readStandard(data: FormData, config: Config): OutputStandard {
  return {
    ...config.output_standard,
    name: String(data.get("std-name")),
    section_titles: Object.fromEntries(
      Object.keys(config.output_standard.section_titles).map((key) => [
        key,
        String(data.get("std-label-" + key)),
      ]),
    ),
    default_export: String(
      data.get("std-default_export"),
    ) as OutputStandard["default_export"],
    enforce_export: data.has("std-enforce_export"),
    paper: String(data.get("std-paper")) as OutputStandard["paper"],
    orientation: String(
      data.get("std-orientation"),
    ) as OutputStandard["orientation"],
    font: String(data.get("std-font")) as OutputStandard["font"],
    font_size: Number(data.get("std-font_size")),
    accent: String(data.get("std-accent")),
    margin_mm: Number(data.get("std-margin_mm")),
    alignment: String(data.get("std-alignment")) as OutputStandard["alignment"],
    line_spacing: Number(data.get("std-line_spacing")),
    paragraph_after_pt: Number(data.get("std-paragraph_after_pt")),
    header_text: String(data.get("std-header_text")),
    footer_text: String(data.get("std-footer_text")),
    page_numbers: data.has("std-page_numbers"),
    columns: JSON.parse(String(data.get("std-columns"))),
    extra_columns: String(
      data.get("std-extra_columns"),
    ) as OutputStandard["extra_columns"],
    table_scope: String(
      data.get("std-table_scope"),
    ) as OutputStandard["table_scope"],
  };
}

/** Load a visible editable example without publishing it. */
export function measurementExample(): void {
  const raw = document.querySelector<HTMLTextAreaElement>(
    '[name="std-columns"]',
  )!;
  raw.value = JSON.stringify(
    [
      {
        key: "item",
        label: "Component",
        aliases: ["item", "part"],
        required: true,
        enabled: true,
      },
      {
        key: "width",
        label: "Width",
        aliases: ["length", "dimension"],
        dimension: "length",
        source_unit: null,
        required: true,
        enabled: true,
      },
    ],
    null,
    2,
  );
  raw.dispatchEvent(new Event("change"));
}
