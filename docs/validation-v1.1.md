# Version 1.1 validation results

This report records bounded local/CI validation for Business Knowledge Workbench by Jason Stys. Release evidence is appended after actual gates complete, not inferred from source existence.

## Local checks

Local Windows Python 3.14.6: **114 tests passed, 88.65% statement coverage** (80% gate retained). Private Chromium/WebKit: **4 browser cases passed**, including genuine registration/WebCrypto, rich DOCX conversion/export, samples, save/lock/reopen, no external requests/browser secrets and 390 px accessibility. Original workflows: **18 local cases passed** across Chromium/WebKit/mobile; six Firefox cases could not launch on this PC. Final Linux CI supplies that missing engine.

Actual packaged Windows executable: **one complete native journey passed in 8.3 seconds**, including a real file download checked for JSON blocks/HTML provenance, not a browser download mock. Early native-test failures involved using a relative URL without an Electron base URL and expecting a browser-only Playwright download event; tests now await the actual local URL and verify Electron's completed download bytes in a disposable directory. No production download gate was bypassed.

Python/npm audits: no known vulnerabilities at candidate validation. Gitleaks 8.30.1: three existing commits and current server/web/desktop/scripts scans clean with redacted output. Generated maps cover **50 authored code files**; the catalog covers **106 tracked files**. Synthetic benchmark: 500 CSV rows / 189 search documents, import p95 **41.327 ms** (budget 2,000 ms), search p95 **3.455 ms** (budget 500 ms). These are local evidence, not SLAs.

Early failures caught and repaired: missing account-screen skip-link target; blob preview rejected by strict embedding policy (replaced by an authenticated scriptless response); accidental export route alias during that preview change (separate export route restored). Assertions and minimum coverage were retained. Local Firefox process launch returned spawn UNKNOWN; Linux browser CI is required for the complete engine matrix. No OS browser/Docker/security repair is attempted.

## Evidence scope

Real converters process supplied fictional text/binary fixtures; AI compatible-provider tests are explicitly mocked with synthetic credentials and no external billing. Installer gates run actual frozen converter dispatch, schema resource and native renderer, not readiness mocks. No claim of public production hosting, adversarial-parser certification, mobile-native installation, signed/notarized binaries, model quality or legal compliance.

Actions artifact uploads default off. Existing retained artifacts are preserved. Run logs and exact release commit/download SHA-256 records provide evidence without growing the full Actions artifact quota.
