# Complete file catalog

Generated from tracked repository paths. Code declarations/parameters and exact lines are in [code-index.md](code-index.md). Runtime databases, credentials, dependencies and temporary test traces are not published.

| File | Responsibility |
| --- | --- |
| [.dockerignore](../.dockerignore) | Limit the container build context to runtime/build inputs. |
| [.gitattributes](../.gitattributes) | LF text checkout and binary Office/PDF/raster preservation across operating systems. |
| [.github/workflows/ci.yml](../.github/workflows/ci.yml) | Automated test/build/container/dependency gates. |
| [.github/workflows/codeql.yml](../.github/workflows/codeql.yml) | Pinned Python and JavaScript/TypeScript CodeQL security analysis. |
| [.github/workflows/packages.yml](../.github/workflows/packages.yml) | Pinned Python and JavaScript/TypeScript CodeQL security analysis. |
| [.github/workflows/release-native.yml](../.github/workflows/release-native.yml) | Pinned Python and JavaScript/TypeScript CodeQL security analysis. |
| [.gitignore](../.gitignore) | Exclude runtime business data, secrets, environments and machine-specific artifacts. |
| [CONTRIBUTING.md](../CONTRIBUTING.md) | Coding, test, documentation and source-safety expectations. |
| [Dockerfile](../Dockerfile) | Multi-stage frontend build and non-root single-origin Python service. |
| [LICENSE](../LICENSE) | MIT terms for this repository; dependencies retain their own licenses. |
| [README.md](../README.md) | Repository overview, capabilities, quick start, validation commands and module summary. |
| [SECURITY.md](../SECURITY.md) | Trust boundaries, vulnerability reporting and production limitations. |
| [compose.yaml](../compose.yaml) | Loopback-only synthetic demo with durable volume and resource/isolation limits. |
| [desktop/main.cjs](../desktop/main.cjs) | Repository configuration/support asset. |
| [docs/adr-private-local.md](../docs/adr-private-local.md) | Architecture decision for private local workspaces. |
| [docs/api.md](../docs/api.md) | API and machine-readable contracts. |
| [docs/architecture.md](../docs/architecture.md) | Architecture and ADR 001: portable, HTML-centered business knowledge. |
| [docs/code-index.md](../docs/code-index.md) | File and code index. |
| [docs/extensions.md](../docs/extensions.md) | Adapting the skeleton and connecting models. |
| [docs/file-catalog.md](../docs/file-catalog.md) | This generated responsibility catalog. |
| [docs/formats.md](../docs/formats.md) | Supported formats, fidelity and platform matrix. |
| [docs/legacy-demo.md](../docs/legacy-demo.md) | Business Knowledge Workbench. |
| [docs/licenses/python-3.12.txt](../docs/licenses/python-3.12.txt) | A. HISTORY OF THE SOFTWARE. |
| [docs/operations.md](../docs/operations.md) | Runbook, installation and release checklist. |
| [docs/private-accounts.md](../docs/private-accounts.md) | Private local accounts and user guide. |
| [docs/private-api.md](../docs/private-api.md) | Private local API. |
| [docs/release-checklist.md](../docs/release-checklist.md) | Private local application release checklist. |
| [docs/releases/v1.1.0.md](../docs/releases/v1.1.0.md) | Business Knowledge Workbench 1.1.0. |
| [docs/reports/pdf-preview.png](../docs/reports/pdf-preview.png) | Recorded local validation/performance or rendered synthetic PDF evidence; see validation.md for scope. |
| [docs/reports/performance.json](../docs/reports/performance.json) | Recorded local validation/performance or rendered synthetic PDF evidence; see validation.md for scope. |
| [docs/reports/validation.json](../docs/reports/validation.json) | Recorded local validation/performance or rendered synthetic PDF evidence; see validation.md for scope. |
| [docs/research.md](../docs/research.md) | Research and coding decisions. |
| [docs/scenarios.md](../docs/scenarios.md) | Synthetic business scenarios and acceptance walkthroughs. |
| [docs/screenshots/catalog.png](../docs/screenshots/catalog.png) | Visually inspected synthetic responsive UI evidence. |
| [docs/screenshots/mobile.png](../docs/screenshots/mobile.png) | Visually inspected synthetic responsive UI evidence. |
| [docs/screenshots/workspace.png](../docs/screenshots/workspace.png) | Visually inspected synthetic responsive UI evidence. |
| [docs/test-plan-v1.1.md](../docs/test-plan-v1.1.md) | Version 1.1 test plan. |
| [docs/validation-v1.1.md](../docs/validation-v1.1.md) | Version 1.1 validation results. |
| [docs/validation.md](../docs/validation.md) | Validation and evidence. |
| [examples/commissioning-pack.docx](../examples/commissioning-pack.docx) | Realistic synthetic source fixture for DOCX extraction and workflow tests. |
| [examples/controller-performance.pdf](../examples/controller-performance.pdf) | Realistic synthetic source fixture for PDF extraction and workflow tests. |
| [examples/custom_ai.py](../examples/custom_ai.py) | Trusted-code adapter example for an operator-supplied callable model. |
| [examples/industrial-sales.csv](../examples/industrial-sales.csv) | Realistic synthetic source fixture for CSV extraction and workflow tests. |
| [examples/installation-note.md](../examples/installation-note.md) | Realistic synthetic source fixture for MD extraction and workflow tests. |
| [examples/laboratory-record.json](../examples/laboratory-record.json) | Realistic synthetic source fixture for JSON extraction and workflow tests. |
| [examples/mixed-measurements.csv](../examples/mixed-measurements.csv) | Realistic synthetic source fixture for CSV extraction and workflow tests. |
| [examples/renewable-specifications.xlsx](../examples/renewable-specifications.xlsx) | Realistic synthetic source fixture for XLSX extraction and workflow tests. |
| [examples/service-record.xml](../examples/service-record.xml) | Realistic synthetic source fixture for XML extraction and workflow tests. |
| [examples/throughput.png](../examples/throughput.png) | Realistic synthetic source fixture for PNG extraction and workflow tests. |
| [index.html](../index.html) | Semantic browser entry, metadata, manifest reference and skip link. |
| [package-lock.json](../package-lock.json) | Exact JavaScript dependency resolution, including platform-optional native build bindings. |
| [package.json](../package.json) | Frontend tooling versions and build/test/format/documentation commands. |
| [playwright.config.ts](../playwright.config.ts) | Four browser targets, isolated database/server and retained test evidence. |
| [playwright.desktop.config.ts](../playwright.desktop.config.ts) | Jason Stys: real frozen Python/Electron integration, no service mock or separate runtime installation. |
| [playwright.private.config.ts](../playwright.private.config.ts) | Jason Stys: isolated private service and three genuine browser engines; no credential traces. |
| [public/icon-192.png](../public/icon-192.png) | Installable PWA metadata/icon asset; no private data is bundled. |
| [public/icon-512.png](../public/icon-512.png) | Installable PWA metadata/icon asset; no private data is bundled. |
| [public/icon.svg](../public/icon.svg) | Installable PWA metadata/icon asset; no private data is bundled. |
| [public/manifest.webmanifest](../public/manifest.webmanifest) | Installable PWA metadata/icon asset; no private data is bundled. |
| [public/offline.html](../public/offline.html) | <!doctype html> |
| [public/sw.js](../public/sw.js) | Shell-only PWA cache. |
| [pyproject.toml](../pyproject.toml) | Python project metadata, dependencies, lint rules and coverage gates. |
| [requirements.lock](../requirements.lock) | Pinned Python application/test/audit dependencies for portable installs. |
| [scripts/benchmark.py](../scripts/benchmark.py) | Measured small-workspace budgets, not hardware-independent performance claims. |
| [scripts/capture.mjs](../scripts/capture.mjs) | Capture synthetic desktop/mobile UI evidence against the local preview. |
| [scripts/code_index.py](../scripts/code_index.py) | Synchronize exact line maps in code headers and the complete file/symbol catalog. |
| [scripts/docx-fixture.mjs](../scripts/docx-fixture.mjs) | Synthetic DOCX with a table, figure and Office Math equation. |
| [scripts/file_catalog.py](../scripts/file_catalog.py) | Generate a one-row-per-tracked-file catalog with useful responsibility summaries. |
| [scripts/fixtures.py](../scripts/fixtures.py) | Generate deterministic synthetic sources and PWA raster icons. |
| [scripts/frozen_entry.py](../scripts/frozen_entry.py) | Jason Stys: frozen private website service and fixed-format conversion child dispatch. |
| [scripts/license_bundle.py](../scripts/license_bundle.py) | Jason Stys: bundle build-environment dependency licenses and notices without collecting user data. |
| [scripts/release_archive.py](../scripts/release_archive.py) | Jason Stys: checksummed portable desktop archives, alongside tested one-click OS installers. |
| [scripts/symbols.mjs](../scripts/symbols.mjs) | Parse TypeScript/JavaScript symbols for documentation without executing source. |
| [scripts/verify.sh](../scripts/verify.sh) | Reproducible local/CI verification. Requires the activated project Python environment and Node 24. |
| [server/__init__.py](../server/__init__.py) | Business knowledge service package. Symbol/variable line locations: docs/code-index.md. |
| [server/accounts.py](../server/accounts.py) | Jason Stys: isolated account/session store; private local authentication and encrypted-vault configuration. |
| [server/ai.py](../server/ai.py) | Swappable, read-only AI adapters with bounded authorized context. |
| [server/analytics.py](../server/analytics.py) | Explainable monthly summaries and bounded baseline forecasts. |
| [server/app.py](../server/app.py) | Same-origin application, authentication, role gates and API orchestration. |
| [server/conversion.py](../server/conversion.py) | Bounded import adapters and canonical HTML generation. |
| [server/exports.py](../server/exports.py) | HTML-first export adapters with predictable, simplified document layout. |
| [server/manage.py](../server/manage.py) | Operator CLI for clean workspaces, user provisioning and consistent backups. |
| [server/models.py](../server/models.py) | Validated configuration and API contracts. |
| [server/permissions.py](../server/permissions.py) | Jason Stys: owner-restricted application data directory permissions, never system-wide policy changes. |
| [server/private_api.py](../server/private_api.py) | Jason Stys: loopback-only real accounts, session-proven vaults, private AI settings and scoped controller. |
| [server/private_cli.py](../server/private_cli.py) | Jason Stys: token-free local account website and frozen service; never execute uploaded documents. |
| [server/private_workspace.py](../server/private_workspace.py) | Jason Stys: exclusive account-scoped document service, encrypted documents/settings, and recoverable shutdown. |
| [server/schema.sql](../server/schema.sql) | Relational records, scoped documents and auditable events. |
| [server/store.py](../server/store.py) | SQLite lifecycle, deterministic synthetic scenarios and ACL queries. |
| [server/units.py](../server/units.py) | Decimal, dimension-aware measurements with provenance. |
| [server/vault.py](../server/vault.py) | Jason Stys: streaming authenticated archives for locked, local business document workspaces. |
| [server/worker.py](../server/worker.py) | Short-lived conversion process with no application credentials. |
| [tests/browser/account-session.ts](../tests/browser/account-session.ts) | Jason Stys: reusable genuine registration, encryption and rich import journey; fictional credentials only. |
| [tests/browser/desktop.spec.ts](../tests/browser/desktop.spec.ts) | Jason Stys: genuine packaged native application conversion, encrypted lock and renderer sandbox checks. |
| [tests/browser/private.spec.ts](../tests/browser/private.spec.ts) | Jason Stys: private website workflow, hostile origins, account isolation and responsive accessibility. |
| [tests/browser/workbench.spec.ts](../tests/browser/workbench.spec.ts) | Cross-browser workflow, accessibility, hostile input and PWA checks. |
| [tests/python/test_adapters.py](../tests/python/test_adapters.py) | Hosted/local/custom AI adapter contracts, product creation and operator tools. |
| [tests/python/test_api.py](../tests/python/test_api.py) | End-to-end API security, persistence and workflow regressions. |
| [tests/python/test_core.py](../tests/python/test_core.py) | Conversion, unit, export and AI contract regression coverage. |
| [tests/python/test_private.py](../tests/python/test_private.py) | Jason Stys: actual private-account, archive, provider, ownership and blocked-execution regression tests. |
| [tsconfig.json](../tsconfig.json) | Strict browser/test TypeScript contracts and module resolution. |
| [vite.config.ts](../vite.config.ts) | Frontend bundling and same-origin API development proxy. |
| [web/main.ts](../web/main.ts) | Accessible workspace UI and explicit API actions. Function/state lines: docs/code-index.md. |
| [web/private.ts](../web/private.ts) | Jason Stys: real local account UI, independent encryption phrase, help and explicit AI consent. |
| [web/style.css](../web/style.css) | Responsive design tokens, layouts and accessible controls. Section lines: docs/code-index.md. |
| [web/types.ts](../web/types.ts) | Shared browser API shapes. Functions/variables and exact lines: docs/code-index.md. |
