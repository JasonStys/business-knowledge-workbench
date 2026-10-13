# Version 1.1 test plan

Author: Jason Stys. Highest risks are cross-account document exposure, parser/input attacks, broken encryption recovery and an installer that cannot run its bundled parsers.

Unit/API layers retain the original measurement, rich extraction, HTML sanitization, archive-bomb, dimension mismatch, sales atomicity, forecasts, role ACL, adapters and export tests. Added actual scrypt/session/recovery, independent-key proof, encrypted source/provider reopen, tag tampering, traversal/device-name rejection, same-account new-session proof, different-account guessed-ID denial, quota recovery, durable throttles, consent revisions and no-secret-echo cases. Real private workers ingest eight binary/text examples including DOCX/PDF/XLSX/PNG; no fake conversion substitutes.

Browser layers exercise original six journeys on Chromium, Firefox, WebKit and mobile layout, plus private registration, WebCrypto, DOCX conversion, authenticated scriptless frame, JSON download, explicit sample import, encrypted save/lock/reopen, logout, no browser-storage secrets, no external default requests, 390 px accessibility/overflow and cross-origin rejection. Failures are not silently skipped. Locally unavailable Firefox is covered on Linux CI without OS security changes.

Native layers run the real frozen Python service in Electron, then the actual OS-packaged executable on Windows, macOS arm64 and Linux x64. The same genuine document journey verifies the frozen converter subprocess dispatch/schema resource, downloads, encryption and lack of Node/process privileges. Final downloaded Windows bytes are independently checksum-verified and tested again after extraction.

CI runs Python 3.12/3.14 on Windows/Linux, dependency/lint/type/format/source-index gates, three browser engines, optional legacy container smoke and Python/TypeScript CodeQL. Native and release jobs test three OS packages before distribution. Large artifacts are opt-in; run logs retain evidence without automatic quota consumption.

No paid/live AI-provider call, malicious-parser penetration assessment, public backend, phone-native installer, signing/notarization or clinical/financial deployment certification is claimed. Provider traffic tests use disclosed synthetic contract mocks. Performance checks are bounded synthetic benchmarks, not production SLAs.

Patch 1.1.1 adds one deterministic initial-navigation/readiness regression on each of the three browser engines. It delays only an actual own-account audit request, verifies navigation/account tools remain disabled while the initial view is incomplete, releases the real request, and completes a real DOCX/export/sample/snapshot journey. This raises the browser matrix to 33 cases without relaxing assertions. Native startup navigation is separately left to its launcher.
