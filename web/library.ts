/* @index-begin
 * @symbol type: LibraryResult L26
 * @symbol function/class: libraryTools L42
 * @symbol variable/parameter: kind L47
 * @symbol variable/parameter: unit L55
 * @symbol function/class: libraryQuery L62
 * @symbol variable/parameter: workspace L63
 * @symbol variable/parameter: offset L64
 * @symbol variable/parameter: params L66
 * @symbol variable/parameter: [key, id] L71
 * @symbol variable/parameter: control L85
 * @symbol variable/parameter: facets L98
 * @symbol function/class: updateFacets L98
 * @symbol variable/parameter: [facet, id] L99
 * @symbol variable/parameter: selected L110
 * @symbol variable/parameter: first L111
 * @symbol variable/parameter: value L116
 * @symbol variable/parameter: option L117
@index-end */
/** Jason Stys: accessible standardized-library filters and bounded result contracts.
 * Functions/variables and exact line locations: docs/code-index.md.
 * Search requests carry only explicit filters; backend ACLs remain authoritative.
 */
import type { Doc } from "./types";

export interface LibraryResult {
  items: (Doc & {
    source_format: string;
    standard_format: string;
    standard_revision: number;
    created: string;
    excerpt: string;
    has_source: boolean;
  })[];
  total: number;
  offset: number;
  limit: number;
  facets: Record<string, string[]>;
}

/** Render finite filter controls; no caller-provided markup is interpreted. */
export function libraryTools(): string {
  return `<form id="library-search"><div class="library-tools">
    <label>Search documents<input id="doc-search" type="search" maxlength="120" placeholder="Part number, phrase, or title"></label>
    <label>Category<input id="doc-category" maxlength="40" list="library-categories" placeholder="All categories"><datalist id="library-categories"></datalist></label>
    <label>Source file type<select id="doc-format"><option value="">All file types</option></select></label>
    <label>Data type<select id="doc-kind"><option value="">All content</option>${["table", "paragraph", "heading", "html", "figure", "equation"].map((kind) => `<option>${kind}</option>`).join("")}</select></label>
    <label>Measurement type<select id="doc-dimension"><option value="">All measurements</option></select></label>
    <label>Access scope<select id="doc-visibility"><option value="">All permitted scopes</option></select></label>
    <label>Extraction review<select id="doc-review"><option value="">All review states</option><option>extracted</option><option>needs-review</option></select></label>
    <label>Table field<input id="doc-field" maxlength="120" list="library-fields" placeholder="e.g. width"><datalist id="library-fields"></datalist></label>
    <label>Field contains<input id="doc-value" maxlength="120" placeholder="e.g. 107.95 mm"></label>
    <label>Minimum (inclusive)<input id="doc-minimum" type="number" step="any" min="-1000000000000000" max="1000000000000000" placeholder="Optional lower bound"></label>
    <label>Maximum (inclusive)<input id="doc-maximum" type="number" step="any" min="-1000000000000000" max="1000000000000000" placeholder="Optional upper bound"></label>
    <label>Numeric comparison unit<select id="doc-unit"><option value="">Unitless number</option>${["mm", "cm", "m", "in", "ft", "g", "kg", "lb", "C", "F", "K", "Pa", "kPa", "bar", "psi", "V", "mV", "Wh", "kWh"].map((unit) => `<option>${unit}</option>`).join("")}</select></label>
    <label>Sort<select id="doc-sort"><option value="title">Title</option><option value="newest">Newest first</option><option value="category">Category</option></select></label>
    <button id="filter" class="quiet" type="submit">Apply filters</button><button type="reset" class="quiet">Clear filters</button></div>
    <p class="muted">Search standardized text and table cells. Choose a table field for text or numeric filters. Numeric bounds match any one cell in that field, converted to the selected unit; unknown or incompatible cells never count as zero. Unitless comparisons match numbers without units. Original attachments and pixels are not OCR-searched; every result respects your permitted scope.</p></form>`;
}

/** Read controls only, with page limits enforced independently by the server. */
export function libraryQuery(
  workspace: string,
  offset: number,
): URLSearchParams {
  const params = new URLSearchParams({
    workspace,
    offset: String(offset),
    limit: "25",
  });
  for (const [key, id] of Object.entries({
    q: "search",
    category: "category",
    source_format: "format",
    kind: "kind",
    dimension: "dimension",
    visibility: "visibility",
    review_status: "review",
    field: "field",
    value: "value",
    minimum: "minimum",
    maximum: "maximum",
    sort: "sort",
  })) {
    const control = document.querySelector<
      HTMLInputElement | HTMLSelectElement
    >("#doc-" + id);
    if (control?.value) params.set(key, control.value);
  }
  if (params.has("minimum") || params.has("maximum")) {
    const unit = document.querySelector<HTMLSelectElement>("#doc-unit")!.value;
    if (unit) params.set("unit", unit);
  }
  return params;
}

/** Populate options from authorized facets with DOM text nodes, not interpolated HTML. */
export function updateFacets(facets: Record<string, string[]>): void {
  for (const [facet, id] of Object.entries({
    categories: "library-categories",
    fields: "library-fields",
    formats: "doc-format",
    dimensions: "doc-dimension",
    visibility: "doc-visibility",
  })) {
    const control = document.getElementById(id) as
      HTMLSelectElement | HTMLDataListElement;
    // Catalog reuses paginated results without the optional business filter form.
    if (!control) continue;
    const selected = control instanceof HTMLSelectElement ? control.value : "";
    const first =
      control instanceof HTMLSelectElement
        ? control.options[0]!.cloneNode(true)
        : null;
    control.replaceChildren(...(first ? [first] : []));
    for (const value of facets[facet] || []) {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = value;
      control.append(option);
    }
    if (control instanceof HTMLSelectElement) control.value = selected;
  }
}
