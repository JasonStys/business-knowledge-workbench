/* @index-begin
 * @symbol function/class: escape L25
 * @symbol variable/parameter: value L25
 * @symbol variable/parameter: character L28
 * @symbol variable/parameter: config L36
 * @symbol function/class: standardFields L36
 * @symbol variable/parameter: standard L37
 * @symbol variable/parameter: select L38
 * @symbol variable/parameter: label L39
 * @symbol variable/parameter: name L40
 * @symbol variable/parameter: values L41
 * @symbol variable/parameter: current L42
 * @symbol variable/parameter: [key, label] L49
 * @symbol variable/parameter: data L58
 * @symbol function/class: readStandard L58
 * @symbol variable/parameter: key L63
 * @symbol function/class: measurementExample L90
@index-end */
/** Jason Stys: safe, data-only output-standard form controls and bounded schema examples.
 * Functions/variables and exact lines: docs/code-index.md. No executable templates are accepted.
 */
import type { Config, OutputStandard } from "./types";

/** Escape all saved labels before inserting them in the authored form structure. */
function escape(value: unknown): string {
  return String(value).replace(
    /[&<>"']/g,
    (character) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        character
      ]!,
  );
}

/** Build finite layout choices and a JSON schema editor; all changes remain drafts until publication. */
export function standardFields(config: Config): string {
  const standard = config.output_standard;
  const select = (
    label: string,
    name: string,
    values: string[],
    current: string,
  ): string =>
    `<label>${label}<select name="std-${name}">${values.map((value) => `<option value="${value}" ${value === current ? "selected" : ""}>${value}</option>`).join("")}</select></label>`;
  return `<fieldset><legend>Documentation and data output standard</legend><p>Only this private account's unlocked owner (or the legacy administrator) can publish or restore standards. Role previews are not coworker permissions.</p><label>Standard name<input name="std-name" value="${escape(standard.name)}" minlength="2" maxlength="80" required></label><div class="config-units">${select("Standard export type", "default_export", ["html", "json", "md", "csv", "docx", "pdf"], standard.default_export)}${select("Paper size", "paper", ["Letter", "A4"], standard.paper)}${select("Page orientation", "orientation", ["portrait", "landscape"], standard.orientation)}${select("Font family", "font", ["sans", "serif", "mono"], standard.font)}<label>Body font size (pt)<input name="std-font_size" type="number" min="10" max="16" value="${standard.font_size}" required></label><label>Heading color<input name="std-accent" type="color" value="${escape(standard.accent)}"></label></div><label class="check"><input name="std-enforce_export" type="checkbox" ${standard.enforce_export ? "checked" : ""}>Restrict document/report exports to the standard file type</label><p>HTML is always generated first internally. Originals and prior revisions are preserved; this delivery policy applies to outputs produced with this revision.</p><h3>Section headings</h3><div class="config-units">${Object.entries(
    standard.section_titles,
  )
    .map(
      ([key, label]) =>
        `<label>${escape(key)} heading<input name="std-label-${key}" value="${escape(label)}" maxlength="80" required></label>`,
    )
    .join(
      "",
    )}</div><h3>Table schema and field order</h3><p>Optional JSON column definitions: key, label, aliases, required, dimension and source_unit. Dimensions use the target units above. Bare numbers are not guessed: declare a source_unit or provide explicit units in each cell. Unknown columns are retained or rejected, never silently dropped.</p><label>Table columns (JSON)<textarea name="std-columns" rows="10" spellcheck="false">${escape(JSON.stringify(standard.columns, null, 2))}</textarea></label><button type="button" id="standard-example" class="quiet">Use measurement-table example</button><div class="config-units">${select("Extra table columns", "extra_columns", ["preserve", "reject"], standard.extra_columns)}${select("Tables covered by schema", "table_scope", ["matching", "all"], standard.table_scope)}</div><p>Matching: enforce on tables with a recognized header and flag other tables for review. All: reject every table that does not satisfy this schema. Empty schema preserves existing table structure. PDF/table extraction still needs review.</p><label>CSV sample for draft preview<textarea name="std-sample" rows="4" maxlength="16000">Component,Width\nPanel,4.25 in\nBracket,8.2 cm</textarea></label><button type="button" id="standard-preview" class="quiet">Preview draft standard</button><p id="standard-preview-status" role="status"></p><iframe id="standard-preview-frame" title="Draft standard preview" sandbox="" hidden></iframe></fieldset>`;
}

/** Read only declared fields; server validation remains authoritative for every draft and publish. */
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
    columns: JSON.parse(String(data.get("std-columns"))),
    extra_columns: String(
      data.get("std-extra_columns"),
    ) as OutputStandard["extra_columns"],
    table_scope: String(
      data.get("std-table_scope"),
    ) as OutputStandard["table_scope"],
  };
}

/** Populate a visible editable example; never automatically save or send it to an AI service. */
export function measurementExample(): void {
  document.querySelector<HTMLTextAreaElement>('[name="std-columns"]')!.value =
    JSON.stringify(
      [
        {
          key: "item",
          label: "Component",
          aliases: ["item", "part"],
          required: true,
        },
        {
          key: "width",
          label: "Width",
          aliases: ["length", "dimension"],
          dimension: "length",
          source_unit: null,
          required: true,
        },
      ],
      null,
      2,
    );
}
