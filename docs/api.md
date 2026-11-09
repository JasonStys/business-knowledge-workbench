# API and machine-readable contracts

> Legacy business-engine/demo reference. Version 1.1 installs the private local account wrapper described in [private-accounts.md](private-accounts.md) and [private-api.md](private-api.md). Old plaintext demo data is separate and is not migrated. Legacy source serving needs explicit `KB_LEGACY_MODE=1`; never expose demo credentials to real records.


Interactive OpenAPI: `/docs`; schema: `/openapi.json`. All `/api/` responses use `Cache-Control: no-store`. Same-origin clients use the HttpOnly `kb_session` cookie. Successful login also returns a CSRF token; send it as `X-CSRF-Token` on authenticated mutations. Do not persist passwords, API keys or session cookies in browser storage.

| Route | Access | Contract |
| --- | --- | --- |
| GET `/api/health`, `/api/bootstrap` | Public | Connectivity; public workspace names, formats and capabilities. |
| POST `/api/login` | Public, rate-limited | `{workspace, username, password}`; database supplies role/account. |
| GET `/api/session`; POST `/api/logout` | Current session | Restore minimal browser state; invalidate session with CSRF. |
| GET `/api/products?workspace=industrial&q=MC-240` | Public/customer/staff | Public catalog or customer-assigned inventory, with normalized specifications. Signed-in workspace cannot be changed by query. |
| POST `/api/products` | Staff + CSRF | Validated ID/name/category/description/exact-cent price/customer/specification text. Generates public HTML-first specification. |
| GET `/api/options` | Staff | Configured customer labels; not publicly exposed. |
| GET `/api/documents` | Scoped | `q`, exact `category`, `sort=title|newest|category`; up to 200 results, ACL first. LIKE wildcard characters are treated literally. |
| GET `/api/library` | Scoped | Metadata-only paginated library, total and authorized facets; see filters below. |
| GET `/api/documents/{id}` | Scoped | Semantic blocks, HTML, warnings, measurements and provenance. |
| GET `/api/documents/{id}/export/{html|json|md|csv|docx|pdf}` | Scoped | Attachment derived from canonical HTML. |
| GET `/api/documents/{id}/source` | Scoped | Original bytes as octet-stream; compilations have no single original. |
| POST `/api/import` | Staff + CSRF | Multipart `file`, `visibility`, `customer`, `category`, optional `dataset=true`. HTML first, then atomic mapped sales import. |
| POST `/api/merge` | Staff + CSRF | `{ids:[...],title}`; 1–12 distinct ordered authorized sources; always internal-only. |
| POST `/api/exports/bundle` | Signed in + CSRF | `{ids:[...]}`; 1–12 distinct IDs, one current workspace; atomic authorization then ZIP of saved-standard exports plus integrity manifest. No original attachments. |
| GET/PUT `/api/config` | Admin; PUT + CSRF | Typed settings, current revision; PUT must match revision/profile. Invalid units/sections/customer removal rejected. |
| GET `/api/report` | Customer/staff | Exact integer USD cents, monthly series, unit counts and optional baseline forecast. |
| GET `/api/audit` | Admin | Latest 50 events for active workspace, no passwords/source text. |
| POST `/api/units` | Public, read-only | `{value:"1",source:"in",target:"mm"}` → `{value:"25.4",unit:"mm"}`. |
| POST `/api/ask` | Signed in + CSRF, AI enabled | `{question}`; bounded authorized context, answer/citations/provider/unverified notice. |
| POST `/api/documents/{id}/vision/{blockIndex}` | Staff + CSRF, AI enabled | Explicit figure transfer and unverified interpretation; no document mutations. |

Error semantics: 401 missing/expired session or invalid credentials; 403 wrong role/CSRF/origin; 404 inaccessible/unknown source (no existence disclosure); 409 stale config, duplicate product, capacity or AI disabled; 413 size; 415 unsupported format/name; 422 invalid/corrupt/over-budget data; 429 login/worker budget; 502 model adapter safely failed. User-facing parser/model errors omit internal paths and credentials. Retry only recoverable states; do not loop on 4xx validation.

## Canonical document schema v1.0

```json
{
  "schema_version": "1.0",
  "title": "example.csv",
  "blocks": [{"kind": "table", "rows": [["part", "width"], ["A", "50.8 mm"]]}],
  "measurements": [{"original": "2 in", "value": "50.8", "unit": "mm", "dimension": "length", "block": 0, "source_start": 0, "source_end": 4}],
  "warnings": [],
  "review_status": "extracted",
  "provenance": {"schema_version": "1.0", "source_name": "example.csv", "sha256": "<64 hex characters>", "config_revision": 1, "conversion_path": ["csv", "html"]},
  "html": "<!doctype html>...",
  "text": "..."
}
```

Blocks may be paragraph, heading, sanitized HTML, table, figure (base64 PNG plus review note), or equation (text plus original Office Math XML). Source offsets are within each original text/cell, not global file offsets. Machine consumers should use block/column context and keep original units, warnings, provenance and ACL scope. They must not interpret `extracted` as verified semantic accuracy.

Sales headers default to `product,customer,month,quantity,revenue_cents`. Column aliases are admin parameters. Rows require a known product/customer assignment, YYYY-MM month and nonnegative bounded integers. Every row validates before transaction commit. The source hash is also recorded in `sales_imports`; changing template revision/visibility cannot multiply sales. Document-only imports and reporting imports have distinct idempotency semantics.

Library filters: `workspace`, literal `q` (120 chars), exact `category`,
`source_format`, `kind`, `dimension`, `visibility`, `review_status`, canonical
`field` and optional `value`, `sort=title|newest|category`, `offset=0..200`,
`limit=1..200` (25 default). Unknown parameters and invalid enums/ranges return
422; a value without a field is invalid. Field matching is exact/case-folded;
values are literal substrings in a data row of that same table column. Response:
`{items,total,offset,limit,facets}`. Items expose ID/title/category/access/timestamp,
source format, standard format/revision, a 240-character standardized excerpt and
source availability, not full HTML or source bytes. Facets cover authorized
categories, source formats, access, canonical fields and dimensions; each list is
capped at 200. Search is standardized-text search, not OCR or original-blob search.

Numeric filters `minimum`, `maximum` and `unit` compare a complete numeric cell
in the selected `field`. Inclusive finite bounds are within ±10^15 with up to
twelve decimal places; unknown units, reversed bounds and bounds without a field
return 422. `unit` must be a supported exact symbol and requires a bound. Empty
unit means genuinely unitless cells, without inference. Text and numeric filters
must match the same data cell. Missing, invalid and incompatible values never
become zero. Stored content and revisions are unchanged by search.

Bundle IDs are 1–80 characters, unique and ordered. Any unavailable member returns
generic 404 before exports begin. Worker contention returns 429; over 32 MiB of
uncompressed output plus manifest returns 413. Successful responses are
`application/zip` attachments, with flat indexed filenames and
`kbw-standardized-bundle/v1` manifest entries. Saved export policies still apply.
Private mode uses `/private/api/exports/bundle` and the same cookie/origin/vault
proof/custom-header controls as other private endpoints.

`POST /api/standards/preview-file` accepts multipart `file` and `config` JSON
(64,000-character maximum), owner/admin + CSRF only. It uses the same supported
format/signature/size checks, two-worker semaphore and 25-second worker deadline
as imports. No configuration/document/sales write or AI call occurs. Private mode
uses `/private/api/standards/preview-file`, requiring exact loopback origin,
`X-KBW-Request:v1`, own cookie and per-session vault proof. Multipart is permitted
only for import and this preview, not arbitrary mutation routes.

Search remains bounded. Add a cursor/FTS contract before lifting the 200-document
scope. UTC SQLite timestamps identify persistence events; monthly sales dates are
calendar periods, not instants.
