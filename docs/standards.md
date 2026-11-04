# Governed documentation and data standards

## Purpose and authority

The workbench standardizes supported documents/data into common units, field
structure, document organization and delivery formats. An output standard is
validated **data**, not a script, executable plug-in, HTML template or CSS string.

Private edition: only an authenticated account with its own vault-proven session
can access the engine. The owner may use Configuration studio for their own
business profiles. Switching an own-account role preview does not invite a team,
share a database or give another local account access. Legacy demo: configuration,
draft preview, history and restoration require the real database `admin` role;
employee/customer/public requests cannot grant themselves that role. Staff can
apply an already published standard to documents they are allowed to see. Shared
business membership and delegation are not implemented by this release.

## Settings and structure

- `units`: target units for length, mass, temperature, pressure, voltage and energy.
  An omitted dimension preserves its source units; choose every relevant target
  when a uniform measurement policy is required. Currency is USD integer cents,
  not a configurable exchange-rate engine.
- `sections`: ordered unique overview/content/measurements/provenance; content
  is mandatory. Omission from the visible document does not remove machine
  provenance or original evidence from storage.
- `output_standard`: name; four section labels; preferred export; optional export
  restriction; Letter/A4; portrait/landscape; sans/serif/mono; 10–16 pt body font;
  six-digit heading color; 10–40 mm margins; paragraph alignment; 1/1.15/1.5/2
  line spacing; 0–24 pt paragraph spacing; bounded plain-text running header/footer;
  DOCX/PDF page numbers; table columns and schema policy.
- `data_columns`: input sales-column aliases, independent of output schema labels.
  Sales validation remains exact/nonnegative integers and known product/customer
  assignments. Reformatting a source must never insert the same sales twice.

DOCX/PDF use the selected page size/orientation and bounded font choices. HTML
uses print-page CSS. JSON/CSV/Markdown retain their natural machine/text structure;
they cannot represent print margins/fonts. Base PDF fonts have limited Unicode
coverage; canonical HTML/JSON remain authoritative for multilingual content.
CSV is a table-only format: a document with no table returns a clear conversion
error rather than an empty file. Choose a compatible document output type.

## Table schema example

Use the visual owner editor to add/remove/reorder/include fields, load its example,
or expand Advanced field definitions for a JSON array of at most 20 columns:

```json
[
  {"key":"item","label":"Component","aliases":["part"],"required":true},
  {"key":"width","label":"Width","aliases":["length"],"dimension":"length","source_unit":null,"required":true},
  {"key":"note","label":"Note","aliases":[],"required":false,"enabled":false}
]
```

Recognized case-insensitive headers become stable machine keys and follow this
order. Human HTML/CSV headings use the configured labels. Optional fields remain
present with an empty cell; disabled fields are excluded. Missing enabled required
headers/values fail. Aliases must
identify one canonical field only; duplicate or ragged source tables fail.
`4.25 in` and `8.2 cm` become `107.95 mm` and `82 mm` for the `mm` target.
Bare `4.25` is rejected for a measurement field unless that field explicitly
declares a source unit, such as `"source_unit":"in"`. This is a human-authored
interpretation, not a claim that the source provided that unit. The untouched
extracted cells and settings snapshot retain that distinction.

CSV, TSV, record-array JSON, extracted DOCX/XLSX/PDF tables and sanitized HTML
tables share this path. HTML surrounding content order is preserved; merged or
nested HTML cells cannot be safely schema-mapped and are rejected. PDF detection
and complex Office content still need source review.

`table_scope=matching` applies the schema only when a recognized header is found;
other tables remain intact and create a review warning. `all` requires every
table to satisfy it. An empty column list disables schema mapping; a nonempty
schema must include at least one enabled field. Extra columns are retained after
standard fields with a warning, rejected, or explicitly omitted with a warning
using `extra_columns=omit`. Disabled fields are recognized and excluded regardless
of extra-column policy. Their units do not require an active target. Exclusion is
not redaction: source bytes and original blocks remain intact; unmatched tables
and surrounding prose can still contain similar information. No type/unit/semantic
inference from AI is used.

## Draft, publish, restore, apply

Draft preview accepts an owner/admin's full configuration and a CSV sample up to
16,000 characters, or multipart configuration plus a supported file up to 4 MiB.
It is local, inert and non-persistent. Invalid drafts produce
validation errors, not partial saves or model requests.

Publication takes the current revision and acquires a SQLite immediate write
transaction. A stale revision returns 409. The new active config, immutable
history snapshot and audit event commit together. History is capped at 250
snapshots per profile; no automatic history deletion occurs. A pre-1.2 vault
receives a snapshot of its actual active settings on initialization; existing
configuration/data are not replaced by new defaults. No downgrade compatibility
claim is made after creating new version-1.2 data; back up the entire closed app
account directory before upgrading.

Restoration is a new publication conditional on the expected current revision,
not rewriting history. An old configuration cannot remove customer IDs that are
still referenced. Standards are stored in the same private encrypted workspace;
provider credentials are not part of their snapshots.

Every new result retains pre-normalization semantic blocks, a full standard
snapshot, revision and SHA-256 settings identity. A hash proves content identity,
not approval or authenticity. Imported originals remain downloadable. New copies
of sources are re-parsed in the existing bounded worker; sales are not replayed.
Compilations use preserved extracted blocks to avoid chained rounding across
unit changes. Legacy compilations without those blocks get an explicit precision
warning; reimport originals for full-fidelity reprocessing. Old documents and
their export policies remain tied to the standard used to create them.

An optional export restriction is enforced on the server against that saved
snapshot, not just in the UI. Current reports use the active presentation and
export policy and the caller's existing sales scope. Their fixed month/quantity/
USD-cents schema is not replaced by an arbitrary product-measurement schema.
Original source downloads and authorized machine-read APIs are not a DRM system.

## API

Private mode prefixes these engine routes with `/private` and requires the
existing cookie, per-session vault proof and mutation boundary headers.

| Route | Authority and effect |
| --- | --- |
| `GET /api/config` / `PUT /api/config` | Owner/admin; read or atomically publish validated settings. |
| `POST /api/standards/preview` | Owner/admin; `{config, sample}` draft CSV, no mutation. |
| `POST /api/standards/preview-file` | Owner/admin + CSRF; multipart `config` JSON and supported `file`; real bounded parser, no persistence or AI. |
| `GET /api/standards/history` | Owner/admin; own profile only, newest first. |
| `POST /api/standards/restore` | Owner/admin; `{revision, expected_revision}`; creates new revision. |
| `POST /api/documents/{id}/standardize` | Authorized staff/owner; creates/reuses a current-standard copy, preserving source scope. |
| `GET /api/report/export/{format}` | Authenticated report scope; canonical HTML first and active delivery policy. |

## Verification

Unit/integration tests cover cross-format equivalent records, schema/header/unit
failures, preserved extras, declared-unit provenance, bounded templates, actual
PDF/DOCX layout, JSON/CSV results, snapshot immutability, source-copy precision,
role spoofing, CSRF, stale updates, history/restore and idempotent old-config
migration. Existing account-isolation/encryption, corrupt-file, rich-parser,
concurrency, sales and model-consent tests remain enabled.

The real owner browser journey previews without publication, publishes a standard,
imports mixed units, inspects PDF bytes, changes units, creates a copy, verifies
the original and restores revision one as a new revision. It is shared with the
actual packaged desktop test. Chromium/Firefox/WebKit cover editor accessibility
and 390-pixel layout. No provider mocks are described as real model inference.

Version 1.3 adds genuine file preview, visual field add/remove/reorder/exclusion,
combined library filters, direct standardized bytes and independent three-industry
oracles over eight tabular input types and six output types. See the
[library guide](library.md) and [current validation](validation-v1.3.md). HTML shows
header/footer once and a page-number explanation; actual DOCX/PDF exports are the
authority for simplified print layout, not a pixel-perfect Word preview.
