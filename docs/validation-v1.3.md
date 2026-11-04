# Validation — searchable standardized library, version 1.3

Jason Stys; 2026-11-04. This report distinguishes actual tests, independent
expected values, UI journeys and platform limits. All companies, accounts and
documents used here are synthetic. Runtime/private account data are excluded
from Git and installer assets.

## Correctness and access evidence

- The complete final Python suite passed **182 cases with 89.70% server coverage**
  after dependency patches and the private multipart-preview regression.
  CI runs the complete suite on Python 3.12/3.14, Ubuntu and
  Windows, retaining the existing 80% gate.
- Twenty-four cases combine three industries with eight genuine tabular inputs:
  CSV, TSV, JSON, HTML, HTM, XLSX, DOCX and PDF. Every normalized table is compared
  to independently authored expected rows, then exported through all six output
  adapters. Genuine source files and exported DOCX/PDF bytes are parsed again.
- Three additional real API journeys cover profile-specific configuration,
  XLSX upload in a credential-stripped worker, persisted normalized records,
  field/value searches, exact original-source downloads and actual DOCX exports.
  Employees can read authorized records but cannot publish or preview standards.
- Library API tests cover literal wildcard/SQL-like terms, paired field/value
  predicates, stable pages, invalid ranges/enums/unknown parameters, inaccessible
  IDs and original/export routes, and hidden counts/categories/field suggestions.
- Draft preview tests verify no inserted record or published revision; private
  multipart tests retain session/vault/origin/custom-header and role gates. Other
  mutation endpoints do not gain general multipart access.
- Legacy settings gain safe defaults. Invalid layout, all-disabled schemas and
  enabled measurement fields without targets fail. Disabled measurement fields
  do not require unused unit targets. Original/source blocks retain excluded data.

## Output and performance evidence

The three generated industry PDFs were rendered with Poppler and visually
inspected for page orientation, table values, readable spacing, running furniture
and page numbers. The DOCX exports passed the Office OOXML validator, with UTF-8
enabled on Windows. Tests inspect their margins, real table cells, header/footer
and page fields. This is simplified document layout; no lossless Word/PDF claim.

The bounded benchmark uses 500 CSV rows, 189 searchable documents and 100 searches.
On this PC, import p95 was 44.308 ms, legacy search p95 4.871 ms and new library
search **including facets** p95 13.421 ms. Budgets remain 2,000/500 ms; hardware
results are not a hosted SLA. See [performance.json](reports/performance.json).
These are in-process conversion/SQLite measurements; worker startup, browser
rendering and vault encryption are outside this microbenchmark.

## Browser, native and CI verification

The shared library journey uses visible controls to add, reorder, remove and
exclude fields; preview an actual CSV without persistence; publish/import; filter
by format/content/dimension/correlated field value; verify downloaded DOCX bytes;
reject a value in the wrong field; clear filters; and inspect mobile overflow and
accessibility. Existing standards/history, rich-document, account isolation,
external-request blocking, delayed-navigation and vault-lock journeys remain.
Native tests run the shared workflow against genuine frozen and packaged
executables, not backend substitutes.

Final local results: **18 legacy/browser-mobile tests passed** (Chromium, WebKit,
mobile Chromium), **10 private browser tests passed** (Chromium/WebKit), and
**one actual Windows packaged-executable journey passed** in 23.3 seconds. The
native journey includes real rich-document download, standards history and the
new library controls. These counts exclude the Firefox launch failures below.

Local Firefox failed to start before app navigation (`spawn UNKNOWN`) even after
reinstalling its official pinned runtime. This is recorded as a local runtime
failure, not a passing application test. The unchanged Firefox engine tests must
pass on the Linux CI runner. Local Chromium/WebKit and mobile emulation remain
separate evidence. No test is skipped or marked expected-failure to hide it.

Required exact-source workflows:

- [Validate workbench](https://github.com/JasonStys/business-knowledge-workbench/actions/workflows/ci.yml): four Python combinations, all browser engines, formatting/source maps, dependency checks and actual container smoke tests.
- [Desktop packages](https://github.com/JasonStys/business-knowledge-workbench/actions/workflows/packages.yml): Windows x64, Linux x64 and macOS arm64, frozen and actual packaged application journeys. PR checks and lock/example change triggers are included.
- [CodeQL](https://github.com/JasonStys/business-knowledge-workbench/actions/workflows/codeql.yml): Python and JavaScript/TypeScript.
- [Native release](https://github.com/JasonStys/business-knowledge-workbench/actions/workflows/release-native.yml): requires those successful workflows for the exact source SHA, rebuilds/tests each platform and publishes checksummed downloads only after all pass.

The release remains draft until the exact-source gates and actual package tests
pass. CI jobs have finite deadlines. Docker on this PC is unchanged; CI validates
the optional container. No Actions cleanup or quota inference is performed.

## Security audits and practical limits

Patched Electron 44.10.2, pypdf 6.21.4, filelock 4.2.1, setuptools 84.1.0,
opentelemetry-api 1.45.1 and compatible npm transitive updates address the high
and Python findings discovered during this work. `pip check` and the locked
Python audit passed. The npm high-severity gate passed; 15 moderate dependency
findings remain in the build-only electron-builder/minimatch chain. That toolchain
is not shipped as application code and uses authored packaging patterns, not user
uploads. Update upstream when compatible fixes are available; do not claim a
zero-advisory npm tree or downgrade to an obsolete builder to silence the audit.

Resolved development findings include duplicate PDF table prose, strict DOCX zoom
settings, the private multipart-preview allowlist and navigation locks restoring
intrinsically disabled pagination/editor controls. Test locator errors were fixed
without removing assertions. Canonical HTML is still first, source evidence is
retained, and exclusion is not redaction.

The app is local/owner-only, unsigned/not notarized, bounded to supported formats
and six measurement dimensions. It is not a hostile-file exploit sandbox, public
team service, universal OCR system or full Word editor. See [library](library.md),
[formats](formats.md) and [privacy](private-accounts.md).
