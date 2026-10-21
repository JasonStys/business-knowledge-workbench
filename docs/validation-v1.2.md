# Version 1.2 validation — governed output standards

Local verification performed 2026-10-21 by Jason Stys's development workflow.
Only fictional fixtures and disposable private accounts were used. Real user
vaults, provider keys, paid model APIs and public hosting were not used.

## Completed local checks

| Check | Actual result and scope |
| --- | --- |
| Python | **150 passed**, 127.39 seconds; Windows, Python 3.14.6. |
| Statement coverage | **88.82%** of 2,129 measured statements; unchanged 80% gate. Subprocess/native execution is not attributed to Python in-process coverage. |
| Original browser workflows | **24 passed**: Chromium, Firefox, WebKit and mobile Chromium layout. |
| Private-account browser workflows | **12 passed**: Chromium, Firefox and WebKit, including the new owner standards workflow, editor accessibility and 390-pixel overflow check. |
| Actual Windows package | **1 passed**, 17.5 seconds; bundled frozen Python service and real packaged Electron executable, not a backend mock. Rich import, actual native JSON download, standard preview/publication, PDF bytes, units/copy/history, vault locking and lack of renderer Node privileges. |
| Static/build | Ruff lint/format, TypeScript strict typecheck, Prettier, Vite production build and generated source/file inventories are required and checked before publication. |
| Dependency checks | `npm audit` and `pip_audit -r requirements.lock`: **0 known advisories** at check time; `pip check`: no broken requirements. |
| Bounded performance fixture | 500 CSV rows, 189 searchable documents, 100 searches. Import p95 **42.079 ms** (2,000 ms budget), search p95 **8.438 ms** (500 ms budget). Machine-specific, not a hosted SLA. |

Exact machine summary: [validation-v1.2.json](reports/validation-v1.2.json).
Measured fixture details: [performance.json](reports/performance.json).
Visible owner controls: [synthetic screenshot](screenshots/standards.png).

## Regression coverage

- CSV/TSV/JSON/DOCX/XLSX/HTML equivalents map to consistent fields and millimeters.
  Explicit dimensional values or declared source units are required; duplicates,
  missing required fields, malformed tables, incompatible/nonfinite values and
  unsupported settings fail instead of inventing information.
- Original cells, source bytes, warnings and immutable settings snapshots survive
  conversion. New copies and mixed-revision compilations use preserved evidence,
  not repeated rounding; sales are not replayed.
- Actual A4 landscape DOCX/PDF dimensions and font settings are inspected. Export
  restrictions are enforced on the backend. Text-only CSV export returns 422.
- Same bytes with different declared input formats do not reuse the wrong parser
  result. Original sales input aliases remain independent of display headings.
- Employee/customer spoofing cannot publish standards. Preview does not persist;
  concurrent publications produce one success/one conflict; stale updates fail.
  Restore creates a new revision; old-config initialization is idempotent.
- Private lock/reopen retains settings encrypted; other accounts cannot see them.
  Existing parser corruption/bounds, scope, vault, consent and lifecycle tests
  remain enabled. No authentication, sandbox or coverage gate was relaxed.

## Failures found during development and resolved

The initial body-less UI POST was correctly rejected by the existing JSON mutation
boundary; the client now sends `{}` with its existing request headers. New preview
status text required precise old test locators. An outdated Firefox runtime failed
to launch on Windows; the pinned Playwright/runtime update passed all three
engines. Native tests now fetch through the renderer's genuine cookie session,
not Playwright's separate HTTP cookie jar. Browser-only viewport emulation was
stalling native screenshot capture; Electron now retains its OS-managed size,
while browser suites still exercise the 390-pixel layout. These failed attempts
are not counted as successful verification.

Dependency audits prompted patched Vite, Pillow, pypdf and certifi pins. A clean
audit is not a complete security assessment. The native application remains
unsigned/not notarized and is not a hostile-file OS sandbox.

## Remote gates and release verification

Inspect the runs for the exact commit, rather than inferring success from this
local report:

- [Validate workbench](https://github.com/JasonStys/business-knowledge-workbench/actions/workflows/ci.yml): Python 3.12/3.14 on Ubuntu/Windows; all browser workflows; audits/inventories; actual container smoke test.
- [Desktop packages](https://github.com/JasonStys/business-knowledge-workbench/actions/workflows/packages.yml): Windows x64, Linux x64 and macOS arm64; both frozen-service desktop and actual packaged-executable journeys.
- [CodeQL](https://github.com/JasonStys/business-knowledge-workbench/actions/workflows/codeql.yml): Python and JavaScript/TypeScript analysis.
- [Native release](https://github.com/JasonStys/business-knowledge-workbench/actions/workflows/release-native.yml): requires successful validation, package and CodeQL runs for the same source commit, tests the newly built packages on all three operating systems, then publishes checksummed binaries.

Large Actions artifacts remain opt-in; no quota limit is inferred from live
artifact-byte totals. The local Docker installation was left unchanged; container
verification belongs to CI. [Requirements review](requirements-review-v1.2.md)
records unsupported universal semantic extraction, team delegation, native mobile
and public-hosting claims explicitly. No paid/live model accuracy is asserted.
