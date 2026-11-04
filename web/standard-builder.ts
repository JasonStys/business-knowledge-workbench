/* @index-begin
 * @symbol function/class: safe L32
 * @symbol variable/parameter: value L32
 * @symbol variable/parameter: c L35
 * @symbol function/class: mountFieldEditor L43
 * @symbol variable/parameter: root L44
 * @symbol variable/parameter: raw L47
 * @symbol variable/parameter: fields L50
 * @symbol variable/parameter: readRows L51
 * @symbol variable/parameter: row L53
 * @symbol variable/parameter: name L54
 * @symbol variable/parameter: checked L58
 * @symbol variable/parameter: v L66
 * @symbol variable/parameter: render L78
 * @symbol variable/parameter: field L83
 * @symbol variable/parameter: index L84
 * @symbol variable/parameter: event L102
 * @symbol variable/parameter: button L103
 * @symbol variable/parameter: target L113
 * @symbol variable/parameter: keys L125
 * @symbol variable/parameter: number L126
 * @symbol variable/parameter: candidate L140
 * @symbol variable/parameter: alias L150
@index-end */
/** Jason Stys: visual data-only standard-field editor, backed by the visible advanced JSON.
 * Functions/variables and exact line locations: docs/code-index.md.
 * This edits a draft only. The server validates and authorizes every publication.
 */
import type { OutputStandard } from "./types";

/** Escape user labels before they become form markup. */
function safe(value: unknown): string {
  return String(value ?? "").replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        c
      ]!,
  );
}

/** Mount bounded row controls without executing templates or discarding the source document. */
export function mountFieldEditor(): void {
  const root = document.querySelector<HTMLDivElement>(
    "#standard-field-editor",
  )!;
  const raw = document.querySelector<HTMLTextAreaElement>(
    '[name="std-columns"]',
  )!;
  let fields: OutputStandard["columns"] = JSON.parse(raw.value);
  const readRows = (): void => {
    fields = [...root.querySelectorAll<HTMLElement>("[data-field-row]")].map(
      (row) => {
        const value = (name: string): string =>
          row.querySelector<HTMLInputElement | HTMLSelectElement>(
            `[data-property="${name}"]`,
          )!.value;
        const checked = (name: string): boolean =>
          row.querySelector<HTMLInputElement>(`[data-property="${name}"]`)!
            .checked;
        return {
          key: value("key"),
          label: value("label"),
          aliases: value("aliases")
            .split(",")
            .map((v) => v.trim())
            .filter(Boolean),
          dimension: value("dimension") || null,
          source_unit: value("source_unit") || null,
          required: checked("required"),
          enabled: checked("enabled"),
        };
      },
    );
    raw.value = JSON.stringify(fields, null, 2);
    raw.setCustomValidity("");
  };
  const render = (): void => {
    root.innerHTML =
      fields
        .map(
          (
            field,
            index,
          ) => `<fieldset data-field-row="${index}"><legend>Field ${index + 1}</legend><div class="config-units">
      <label>Field key ${index + 1}<input data-property="key" value="${safe(field.key)}" maxlength="40" pattern="[a-z][a-z0-9_]{0,39}" required></label>
      <label>Field label ${index + 1}<input data-property="label" value="${safe(field.label)}" maxlength="60" required></label>
      <label>Field aliases ${index + 1}<input data-property="aliases" value="${safe(field.aliases.join(", "))}" maxlength="480" placeholder="Comma-separated source headings"></label>
      <label>Field measurement ${index + 1}<select data-property="dimension"><option value="">Text / other data</option>${["length", "mass", "temperature", "pressure", "voltage", "energy"].map((value) => `<option ${field.dimension === value ? "selected" : ""}>${value}</option>`).join("")}</select></label>
      <label>Field source unit ${index + 1}<input data-property="source_unit" value="${safe(field.source_unit)}" maxlength="5" placeholder="Only for bare numbers"></label>
      <label class="check"><input type="checkbox" data-property="enabled" ${field.enabled !== false ? "checked" : ""}>Include field ${index + 1} in output</label>
      <label class="check"><input type="checkbox" data-property="required" ${field.required ? "checked" : ""}>Require field ${index + 1}</label></div>
      <div class="button-row"><button type="button" data-move="up" ${index === 0 ? "disabled" : ""}>Move field ${index + 1} up</button><button type="button" data-move="down" ${index === fields.length - 1 ? "disabled" : ""}>Move field ${index + 1} down</button><button type="button" data-move="remove">Remove field ${index + 1}</button></div></fieldset>`,
        )
        .join("") ||
      "<p>No enforced table fields. Source table structure is preserved.</p>";
    document.querySelector<HTMLButtonElement>("#standard-add-field")!.disabled =
      fields.length >= 20;
  };
  root.addEventListener("input", readRows);
  root.addEventListener("change", readRows);
  root.addEventListener("click", (event) => {
    const button = (event.target as HTMLElement).closest<HTMLButtonElement>(
      "button[data-move]",
    );
    if (!button || button.disabled) return;
    const index = Number(
      button.closest<HTMLElement>("[data-field-row]")!.dataset.fieldRow,
    );
    readRows();
    if (button.dataset.move === "remove") fields.splice(index, 1);
    else {
      const target = index + (button.dataset.move === "up" ? -1 : 1);
      if (!fields[index] || !fields[target]) return;
      [fields[index], fields[target]] = [fields[target]!, fields[index]!];
    }
    raw.value = JSON.stringify(fields, null, 2);
    render();
  });
  document
    .querySelector("#standard-add-field")!
    .addEventListener("click", () => {
      readRows();
      if (fields.length >= 20) return;
      const keys = new Set(fields.map((field) => field.key));
      let number = fields.length + 1;
      while (keys.has("field_" + number)) number++;
      fields.push({
        key: "field_" + number,
        label: "New field",
        aliases: [],
        required: false,
        enabled: true,
      });
      raw.value = JSON.stringify(fields, null, 2);
      render();
    });
  raw.addEventListener("change", () => {
    try {
      const candidate: OutputStandard["columns"] = JSON.parse(raw.value);
      if (
        !Array.isArray(candidate) ||
        candidate.length > 20 ||
        candidate.some(
          (field) =>
            !field ||
            typeof field.key !== "string" ||
            typeof field.label !== "string" ||
            !Array.isArray(field.aliases) ||
            field.aliases.some((alias) => typeof alias !== "string"),
        )
      )
        throw Error("Invalid editor rows");
      fields = candidate;
      render();
      raw.setCustomValidity("");
    } catch {
      raw.setCustomValidity(
        "Enter a JSON array of at most 20 field definitions; server validation is still required.",
      );
    }
  });
  render();
}
