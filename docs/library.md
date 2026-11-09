# Standardized file library

Business Knowledge Workbench 1.4 by Jason Stys stores supported original files
alongside their standardized semantic blocks, canonical HTML, measurements,
settings snapshots, warnings and identity hashes. The library presents these
records without downloading every full document into the browser.

## Upload, inspect and download

1. Unlock your account. Choose its industrial, renewable or laboratory profile.
2. Publish the profile's standard in Configuration studio if you are its owner.
3. In Business workspace choose a Source file and category/access labels, then
   Import & standardize. Staff may import; customer/catalog views cannot.
4. Review the canonical preview and extraction warnings. Inspect original source
   when reading order or table detection is uncertain, especially for PDFs.
5. Download the standard format from the library row, or open Preview for original
   source, provenance and permitted alternate exports. Export restrictions follow
   the document's saved standard, even after the current standard changes.

New private accounts start empty. Loading the optional examples is explicit.
Own-account customer/employee tabs are preview perspectives, not an invitation
system. In the separate legacy role deployment, the server's database identity
determines actual access. Counts and suggestions must not reveal hidden records.

## Search examples

| Need | Filters |
| --- | --- |
| Find an inspection file | Search documents `inspection`, category `Metrology`, source file type `csv`. |
| Find standardized lengths | Data type `table`, measurement type `length`. |
| Find a specific value in a field | Table field `width`, Field contains `107.95 mm`. A match in `mass` or an unrelated table cannot satisfy this. |
| Manufacturing tolerances across standards | Table field `width`, Minimum `100`, Maximum `110`, numeric comparison unit `mm`. `4.25 in`, `107.95 mm` and `10.795 cm` are equivalent. |
| Renewable asset capacity band | Table field `capacity`, Minimum `40`, Maximum `50`, unit `kWh`; `42500 Wh` is in range. |
| Laboratory temperature range | Table field `temperature`, Minimum `0`, Maximum `40`, unit `C`; `32 F` is on the inclusive lower boundary. |
| Review ambiguous extraction | Extraction review `needs-review`, optionally source file type `pdf`. |
| Browse assigned customer evidence | Customer perspective with any filters; inaccessible sources, counts, categories and field names remain excluded. |

Filters combine with AND. Text search is a case-folded literal substring over
title and standardized text; `%`, `_`, backslashes and SQL fragments are not
query syntax. Category/source/access/review filters are exact. Table field is an
exact case-insensitive **canonical key**, suggested by a datalist; Field contains
is a substring in a data row of that same column. Values require a field.
Numeric bounds also require a field; both bounds are optional, but a comparison
unit requires at least one. Minimum must not exceed maximum. All conditions on
one field must match the **same cell**, not different rows. Units are explicit
and dimension-compatible; a unitless query matches only unitless numbers. An
unparseable or missing cell does not become zero. This is an any-matching-row
document filter, not an aggregate, count of matching rows or certification of
measurement accuracy. Bounds are finite, within ±10^15 and at most twelve decimal
places. Conversions use the application's six-decimal canonical precision.
Earlier records keep their saved values and standard; search converts comparison
values without updating their content. Originals, excluded fields and pixels are
not queried. Unit symbols are case-sensitive (`mV`, `kWh`, `C`).
Clear filters resets the form. Sort supports title, newest and category, with an
ID tie-breaker. Previous/Next navigate 25-row pages; the API permits 1–200 rows
and offsets 0–200 within the existing 200-document profile cap.

## Gather standardized files

Select one to twelve permitted files across pages, then Download selected files
(ZIP). Clear selection resets the set; switching account/profile/view clears it.
Filtering does not clear selections, so the count may include hidden result pages.
An inaccessible or missing member rejects the whole request before file generation;
remove stale selections or clear and select again. Each file follows its own saved
standard and export restriction, not the current configuration. A bundle is not a
compilation: it preserves individual files and does not merge tables or replay sales.

ZIP entries have flat indexed filenames. `manifest.json` binds each selected ID,
title, output type, byte count, SHA-256 and saved standard revision/digest to this
download. Verify hashes after extraction to detect accidental byte changes. They
are integrity checks, not a publisher signature or permission grant. ZIP/DOCX time
metadata can differ on later downloads; binary reproducibility is not promised.
Original attachments, login data and AI keys are excluded, but standardized outputs
are plaintext and can contain sensitive business information. Protect downloaded
copies separately. The server allows two concurrent bundles and at most 32 MiB of
uncompressed files plus manifest. Busy workers return 429; oversized bundles 413.

Search examines saved standardized content, not original attachments, image
pixels, OCR or semantic embeddings. Excluded fields remain in original/source
evidence but do not become standardized field suggestions. Disabled/unknown
columns are excluded only where the selected table-schema policy applies;
unmatched tables and surrounding prose are preserved and flagged. This is not a
confidentiality redaction system. JSON downloads include source evidence.

## Format and field customization

Configuration studio provides a visual editor for up to 20 fields: key, displayed
label, aliases, required/optional, measurement dimension, declared source unit,
included/excluded, order and removal. Enable at least one field, or remove all
fields to retain source structure. Removed fields become unknown inputs; choose
Extra table columns = `omit` to remove unknown fields from standardized tables.
`preserve` retains and warns; `reject` stops incompatible imports. Omitted source
cells remain preserved, and explicit omissions produce review warnings.

Choose target units only for relevant dimensions (Keep source units disables a
target). Every enabled typed field needs a matching target. A bare number needs
an explicitly declared source unit; the app must not guess it. Section order and
headings are independent from table fields and sales-input aliases.

Word-like controls include paper/orientation, font/size/color, 10–40 mm margins,
alignment, line/paragraph spacing, plain-text running header/footer and DOCX/PDF
page numbers. These are validated finite settings, not full Word editing or
uploaded executable templates. HTML previews are not paginated Word simulations:
they show furniture once and explain page numbering. Inspect actual exports when
pagination matters. JSON/CSV/Markdown preserve content, not print geometry.

Select a supported file for Preview draft standard to exercise its genuine parser
under the proposed settings, or leave that field empty to use the CSV sample.
Preview is bounded, local and non-persistent; it does not call AI, save settings,
create a document or replay sales. Publication creates a new revision. Existing
records keep their old standard until you create a current-standard copy.

## Implementation boundaries

`server/library.py` binds query values and restricts JSON paths/sort fragments to
authored constants. ACL predicates precede counts, results and facet suggestions.
Each search scans bounded authorized content; facets describe the entire allowed
profile, not only current matches. Each suggestion list is capped at 200 values.
This is a small-workspace design; introduce indexed, tenant-scoped full-text
search and measured cursor semantics before increasing the document cap.

The HTTP API is documented in [api.md](api.md). Authentication, independent vault
proof, same-origin mutation headers, parser deadlines and source-download ACLs
remain enforced. Standards authority is described in [standards.md](standards.md).

## Realistic reproducible demonstrations

[industry-cases.json](../examples/industry-cases.json) contains independently
authored source and expected values for three fictional businesses:

- Manufacturing inspection: `4.25 in → 107.95 mm`, `2.2 lb → 0.997903 kg`;
  supplier notes excluded.
- Renewable equipment records: `42500 Wh → 42.5 kWh`, `48000 mV → 48 V`;
  legacy tags omitted.
- Calibration laboratory: `104 F → 40 C`, `1 bar → 100 kPa`,
  `101325 Pa → 101.325 kPa`; technician notes omitted.

Tests create genuine CSV, TSV, JSON, HTML, HTM, XLSX and PDF sources; tracked DOCX
fixtures are independently generated by `node scripts/industry_fixtures.mjs`.
Every case checks the entire normalized table, retained originals and six export
types. API journeys cover all three profiles plus real staff authorization;
browser and native journeys use visible controls and actual downloaded bytes.
Synthetic output PDFs/DOCX for inspection are written to ignored
`artifacts/industry-outputs/`; no real account data is committed.
