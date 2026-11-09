# Quantitative search and evidence-pack validation

Jason Stys, 2026-11-09. Synthetic local accounts and disposable databases only;
existing private account stores and user documents were not changed.

## Delivered behavior and independent checks

Numeric library bounds use one complete cell in the chosen canonical column,
with explicit compatible units and inclusive Decimal comparisons. Text and range
conditions cannot match different rows/columns. Hand-known values cover inches,
centimeters, pounds, offset temperatures, voltage, pressure, energy and unitless
numbers. Missing/malformed/incompatible values never become zero. Tests exercise
old/new standard revisions without rewriting earlier measurements, invalid ranges,
unknown units/precision and customer scope. Scientific notation now converts as
one quantity rather than accidentally recognizing an exponent suffix; real import,
search and exported HTML prove `5e-3 V = 0.005 V = 5 mV`.

Selected-file ZIPs authorize every ID in one workspace-scoped snapshot before
generating any output. Tests independently inspect archive members, order, saved
HTML/DOCX policies, converted text, byte counts and SHA-256 hashes. Mixed hidden
selections never reach generation. Repeated/oversized IDs, missing sessions/CSRF,
worker contention, output budgets and malicious path-like titles are tested.
Original attachments and account material are excluded; outputs remain plaintext.

## Observed local gates

- **228 Python tests passed**, **89.87% statement coverage**, above the unchanged
  80% gate. Numeric search/predicate modules are fully covered. Existing realistic
  manufacturing, renewable-energy and calibration cases in `test_industries.py`
  cover multiple source/output types, schema customization, original preservation
  and role boundaries; the new tests extend rather than replace them.
- Strict TypeScript/Vite production build, Ruff lint/format, Prettier and source
  navigation/catalog checks form the release gates. All edited code is covered by
  the applicable API or real user-journey checks.
- Private browser journeys: **10 passed** across Chromium/WebKit. Legacy-role and
  mobile journeys: **18 passed** across Chromium/WebKit/mobile. The new owner
  journey actually edits/publishes a standard, previews/imports a file, combines
  text with centimeter range bounds over saved millimeter data, downloads real
  ZIP bytes and clears selection, including accessibility/390px overflow checks.
- Windows' installed Playwright Firefox runtime failed to launch (`spawn UNKNOWN`)
  before page code in all eleven Firefox attempts. These are environment failures,
  not passing tests. The unchanged mandatory Linux Firefox lane remains required;
  no browser project or OS protection was disabled to hide this limitation.
- The actual packaged Windows executable passed its full disposable-account
  journey, including rich-file conversion, standards, quantitative filters, a real
  native ZIP download, encrypted lock/reopen and no renderer Node privileges.
  This does not claim local Linux/macOS native execution; their packaged-app
  workflows remain mandatory.
- Existing bounded benchmark passed: 500-row conversion p95 **58.141 ms**, simple
  search p95 **8.017 ms**, faceted library p95 **25.948 ms**, against the existing
  2000/500 ms budgets. Host-load-dependent observations, not a production SLA.
- Python dependency audit found no known vulnerabilities. A narrow tested
  minimatch override to 11.0.1 fixed the current build-tool advisory; npm audit
  then reported **zero vulnerabilities**. The [upstream advisory](https://github.com/advisories/GHSA-g3hv-75wg-m249)
  identifies the patched version. No forced toolchain downgrade or audit ignore.

One local pytest cache-write warning affected only optional test caching; all
assertions and coverage completed. No real provider calls, hosting changes,
private account exports or installer replacement were used for these checks.

## Practical limits and hosted validation

This remains a local owner-account application, not shared business hosting.
Ranges search standardized table cells, not pixels/original blobs or inferred
units; conversions use six-decimal canonical precision. Bundles hold 1–12 files,
two concurrent workers and 32 MiB uncompressed content plus manifest. They are
neither encrypted nor signed, and do not certify source semantics.

The exact source must pass existing Python portability, three-browser/private,
CodeQL, container and three-OS genuine packaged-app Actions before merge/release.
This report records local evidence; authoritative hosted results are linked from
the pull request and portfolio maintenance report, without manufacturing a
passing result for an unavailable local runtime.
