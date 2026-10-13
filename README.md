# Business Knowledge Workbench

A private, local-first document and data application by **Jason Stys**. Import business documentation, normalize units, search evidence, manage products, combine sources, export HTML-first documents, and review sales trends. Version **1.1.0** adds real local accounts, independently encrypted workspaces and native desktop downloads to the original reference application.

[Source and Actions](https://github.com/JasonStys/business-knowledge-workbench) · [Downloads](https://github.com/JasonStys/business-knowledge-workbench/releases/tag/v1.1.0) · [Contact Jason on LinkedIn](https://www.linkedin.com/in/jason-stys-31b30b351/)

## Install and start

Download a release for your OS, verify its SHA-256 record and launch the app. The Windows per-user setup is one click; a portable ZIP is also provided. macOS arm64 and Linux x64 packages are available. Native packages include Python, the document service and the UI—no terminal setup is needed for normal use. Builds are **unsigned / not notarized**; no claim of store approval or universal hardware support.

Choose **Open local website** from the desktop menu to use the same app in a browser. The service binds only `127.0.0.1` on an automatically selected port. There is no public hosted website, paid hosting, telemetry or Jason-operated account server. A phone cannot connect to another device's loopback address; this release has responsive web layouts, not native mobile installers.

Create an alias and login password, privately save the once-shown login recovery code, then choose a **different vault phrase**. Forgotten vault phrases cannot be recovered or reset by Jason. See [private accounts and user guide](docs/private-accounts.md).

## Main features

- Fifteen supported extensions: text, Markdown, sanitized HTML, CSV/TSV, JSON, XML, DOCX, XLSX, PDF and raster images. Original evidence, semantic blocks, extraction warnings and hashes are retained.
- Canonical **HTML first**, then HTML, JSON, Markdown, CSV tables, DOCX or PDF export. Graphs/images are preserved where supported, not universally understood; read the [format limits](docs/formats.md).
- Decimal-based measurement normalization with dimension validation; `4.25 in → 107.95 mm`, `104 F → 40 C`. Configuration revisions preserve provenance.
- Product catalog, customer subset preview, business reporting and administrator configuration views. These are previews within **your own** account, not a coworker invitation or shared-tenant permission system.
- Explicit opt-in fictional industrial equipment, renewable energy and laboratory supply scenarios. New accounts start with **no products, sales, sources or demo users**.
- Search, filtering, sort, ordered internal-only compilations, atomic sales imports with duplicate prevention, exact-cent reports, accessible graphs and labeled baseline forecasts.
- Optional read-only AI: offline extractive reference by default; explicitly connect an own local OpenAI-compatible server or the official HTTPS chat endpoint. Own keys are encrypted with documents when locked, never returned to the UI. External source transmission requires consent for the selected destination revision.
- Real local login, scrypt password hashes, expiring HttpOnly cookies, same-origin/custom-header request gates, separate session vault proof, human-idle locking, encrypted snapshots, login recovery and current-password-confirmed own-account deletion.
- Same-origin scripts, no third-party assets or ad integrations, scriptless document previews and sandboxed native renderer with no Node/preload privileges. These controls do not defeat malware or a compromised OS/browser extension.

## Privacy and practical limits

Each account's locked document database and model settings are stored in an AES-256-GCM archive outside Git and installation files. While unlocked, the trusted local service temporarily uses plaintext files and an in-memory key. The OS owner/administrator or malware can inspect active data; this is **not zero-knowledge or protection from a compromised device**. Jason has no app backdoor or automatic remote data access.

Lock or sign out before switching accounts. Save an encrypted snapshot, then close the application before backing up the **entire** private account directory. A downloaded snapshot alone lacks account/key configuration. Plaintext exports and old developer/demo databases need separate protection. Existing demo/legacy data is neither imported nor erased.

Supported uploads are bounded to 4 MiB and 200 documents per business profile. Parsing uses timed credential-stripped child processes, not an antivirus or complete OS exploit sandbox. Do not upload files from untrusted attackers on a sensitive workstation; hostile-parser containment/CDR and shared business hosting need a separate deployment design. There is one unlocked account engine at a time. See [architecture decision](docs/adr-private-local.md), [security policy](SECURITY.md) and [release checklist](docs/release-checklist.md).

Hosted model providers can retain deliberately transmitted content under their policies. Official chat requests set `store: false`; that is not a promise of zero provider retention. No live API keys or paid model calls are required by the test suite.

## Run from source

Developer setup requires Node 24 and Python 3.12–3.14:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.lock -e .
npm ci
npm run build
.venv\Scripts\python.exe -m server.private_cli
```

The CLI opens the local account website. Keep its process running. A trusted operator can set `KBW_ACCOUNT_DATA` to a dedicated empty test directory; never point it at unrelated files. The [legacy synthetic demo](docs/legacy-demo.md) is separate and requires explicit `KB_LEGACY_MODE=1` and `KB_DEMO=1`; never expose it to real records. Docker is optional for demo CI, not required by the installed app.

## Tests and documentation

```powershell
.venv\Scripts\python.exe -m ruff check server scripts tests/python
.venv\Scripts\python.exe -m ruff format --check server scripts tests/python
npm run format:check
.venv\Scripts\python.exe scripts/code_index.py --check
.venv\Scripts\python.exe scripts/file_catalog.py --check
.venv\Scripts\python.exe -m pytest -q
npm run build
npx playwright install chromium firefox webkit
npm test
npm run test:private
npm audit --audit-level=high
.venv\Scripts\python.exe -m pip_audit -r requirements.lock
```

[Validation results](docs/validation-v1.1.md), [test plan](docs/test-plan-v1.1.md) and [private API](docs/private-api.md) distinguish actual conversions/browser/native tests from provider mocks and unsupported deployments. CI retains logs; large Actions artifacts are **opt-in** through `KBW_UPLOAD_CI_ARTIFACTS=true`. Tested downloads go to Releases instead of consuming Actions artifact quota.

## File responsibilities and language choices

| Area | Responsibility |
| --- | --- |
| `web/main.ts`, `types.ts`, `style.css`, `index.html` | Typed document/product/reporting views, accessible HTML, responsive styling and escaped rendering. |
| `web/private.ts` | Account forms, browser key derivation, help, own AI settings, consent and human-activity signals. |
| `server/accounts.py`, `permissions.py`, `vault.py` | Local authentication/session/recovery hashes, dedicated OS-user permissions and streamed authenticated snapshots. |
| `server/private_api.py`, `private_workspace.py`, `private_cli.py` | Exact-loopback boundary, account-isolated document engine, serial lifecycle/idle recovery and local launch. |
| `server/app.py`, `models.py`, `store.py`, `schema.sql` | Preserved business API, validation, relational integrity, scoped searches and synthetic seeding. |
| `server/conversion.py`, `worker.py`, `units.py` | Supported rich-format parsers, bounded child conversion and exact normalization. |
| `server/exports.py`, `analytics.py`, `ai.py` | HTML-derived exports, explainable reporting and read-only model contracts. |
| `desktop/main.cjs` | Electron shell with an owned frozen service, denied external navigation/popups and graceful sealing. |
| `scripts/` | Frozen entry, licenses/checksums, fixture/benchmark and exact line/file inventories. |
| `tests/`, `playwright*.config.ts` | Real parser/API/crypto/role regressions, browser journeys and native packaged-app tests. |
| `public/`, `examples/` | Shell-only legacy PWA assets and clearly fictional sample evidence; no user data. |
| `.github/workflows/`, root configuration | Reproducible dependency/build/CI/package/release gates and optional legacy container. |
| `docs/` | Usage, limits, architecture, contracts, validation/release evidence and per-file/source maps. |

Python uses its mature document ecosystem, TypeScript provides typed browser interactions, SQL provides transactional business persistence, HTML/CSS keep outputs inspectable, and JavaScript powers the isolated desktop shell. [The complete file catalog](docs/file-catalog.md) summarizes each tracked file; [the generated code index](docs/code-index.md) maps every authored code file's functions/classes/variables to exact lines. Regenerate inventories after source edits.
