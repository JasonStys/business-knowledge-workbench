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

## Validated release source

The following 1.1.0 evidence is retained as history. Patch 1.1.1 fixes the asynchronous-view race identified during final review; its new delayed-response regression passes locally in Chromium and WebKit. Patch release evidence is recorded below after the new immutable source and downloads are validated.

Immutable release source: `f3676bfb40cbff170bb22114715275af2b402c6d`.

| Gate | Verified result |
| --- | --- |
| [Validate workbench 38355646906](https://github.com/JasonStys/business-knowledge-workbench/actions/runs/38355646906) | Success, attempt 2. Four Python OS/version jobs, container smoke and all 30 browser cases; original assertions/80% coverage gate retained. |
| [Desktop packages 38355646825](https://github.com/JasonStys/business-knowledge-workbench/actions/runs/38355646825) | Success, all three OS jobs. Actual frozen service and actual packaged executable tested on each OS. |
| [CodeQL 38355646811](https://github.com/JasonStys/business-knowledge-workbench/actions/runs/38355646811) | Success, Python and TypeScript; no open code-scanning alerts at release review. |

Attempt 1 of the final validation run had one Chromium preview assertion timeout; the other five private cases and 24 original cases passed. The unchanged source passed a fresh failed-job rerun. The first failure is retained, not deleted or presented as an uninterrupted clean first pass; transient preview readiness is a reliability watchpoint. Earlier native run 38354790877 exposed a Linux executable-name mismatch and a macOS test navigation race. The actual Linux path was corrected; native helpers no longer reload a window during the launcher's pending loadURL. Subsequent three-OS native checks pass.

Source history scan now covers six commits with no Gitleaks findings. Account artifact bytes remain **255,402 in five artifacts** for this repo; account-wide artifact bytes **564,608,894**, separate cache bytes **6,228,890,969** at the read-only check. GitHub's billing meter showed **0.5 GB / 0.5 GB included (100%)**, **$0 billable after discounts**. These billing/cache/retained-byte measurements are separate; no cleanup was authorized or performed.

## Published download and installed verification

[Release workflow 38356820253](https://github.com/JasonStys/business-knowledge-workbench/actions/runs/38356820253) passed all five jobs: exact-source gate, three tested OS packages and final publication. [Release v1.1.0](https://github.com/JasonStys/business-knowledge-workbench/releases/tag/v1.1.0) contains six binaries/portable archives and six SHA-256 records. All records match GitHub's corresponding binary asset digests, including the provider's canonical space-to-dot filenames.

The independently downloaded Windows portable ZIP is **205,635,687 bytes**, SHA-256 `0d041f72f25b321b3b80c1fefcad5015fd8a7fa5da0eda41d11faf6db1acb78d`. It was verified before extraction to `C:/Users/jason/Documents/Codex/Applications/BusinessKnowledgeWorkbench-1.1.0`. The exact downloaded executable passed the genuine native journey again (**one case, 9.1 seconds**), including real JSON download bytes and no renderer Node/process access. Synthetic accounts/logs used separate disposable directories, not the live account root.

The installed app was then launched normally with its empty private root. Its local website returned ready/private-local-accounts/1.1.0 metadata and visibly showed the blank account-creation screen. The [account screenshot](screenshots/accounts.png) contains no entered credential or real account information. No real user account/API credential was created by the tester. This final documentation/screenshot update does not change the tested runtime. Current inventories contain 50 authored code maps and 108 tracked-file summaries.

## Patch 1.1.1 readiness correction

Final review turned the prior preview timeout into deterministic delayed-response coverage. An initial view could insert navigation before its reads finished; a subsequent workspace could likewise display import controls while its library read was pending. A newer view could be overwritten, or a busy action could be ignored. Navigation and newly inserted action buttons now remain disabled while a view/action is incomplete. A child-list observer applies the same gate to asynchronously inserted controls; it does not observe its own attribute writes. Private lock/sign-out stay available. A disconnected account-tools target cannot overwrite a newer shell.

The delayed test holds actual audit and library reads, asserts navigation/import controls are disabled, releases the real reads, and completes a genuine DOCX/export/snapshot journey. It adds three configured cases (one per browser), not a mocked converter or a relaxed timeout. An intermediate candidate exposed the action-button half of the race in Linux native and Chromium tests; those failures are retained. The corrected patch passed all 33 browser cases on its **first CI attempt**.

Immutable patch runtime source: `fd07b73a77d4559c18c84f368050b9f06f4fc4f8`.

| Patch gate | Verified result |
| --- | --- |
| [Validate workbench 38359644444](https://github.com/JasonStys/business-knowledge-workbench/actions/runs/38359644444) | Success, first attempt, all six jobs; 114 Python cases per tested environment and 33 browser cases. |
| [Desktop packages 38359644512](https://github.com/JasonStys/business-knowledge-workbench/actions/runs/38359644512) | Success, all three OS jobs; frozen and actual packaged app tested on each. |
| [CodeQL 38359644481](https://github.com/JasonStys/business-knowledge-workbench/actions/runs/38359644481) | Success, both languages; no open alerts at patch review. |

The 1.1.0 downloads remain unchanged for provenance. Patch 1.1.1 uses the same account directory and authenticated archive format; no credentials/data migration or automatic deletion is performed.

[Patch release run 38360416917](https://github.com/JasonStys/business-knowledge-workbench/actions/runs/38360416917) passed all five jobs and published [v1.1.1](https://github.com/JasonStys/business-knowledge-workbench/releases/tag/v1.1.1). All six patch checksum records match their corresponding GitHub binary digests. The independently downloaded Windows ZIP is **205,635,334 bytes**, SHA-256 `2a124428272fa1cce52cfafc7fdbfeb377b98f8bbb6a67f623b365389ecc6780`.

That exact ZIP was verified before extraction to `C:/Users/jason/Documents/Codex/Applications/BusinessKnowledgeWorkbench-1.1.1`. Its executable passed the complete genuine native journey again (**one case, 8.8 seconds**). An additional disposable native check imported the rich DOCX and confirmed its embedded figure decoded with natural width **640 pixels**, then locked the workspace. No live model/API key was used.

The provisional 1.1.0 process was stopped; its parent-monitor cleanup completed and no active recovery directory remained. Its installation and release files were preserved. The installed 1.1.1 application was launched normally and its website visibly shows the blank local account form. Runtime account files remain outside Git/installation, and no actual user credential was created by the tester. Temporary source preview was stopped; other previously installed applications were not modified. Final documentation is a metadata-only follow-up to the immutable tested runtime; inventories cover 50 authored code maps and 110 tracked files.
