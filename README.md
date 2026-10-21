# Business Knowledge Workbench

A private, local-first **document and data standardization application** by **Jason Stys**. Its main job is to turn supported business files from different sources into a consistent, inspectable representation: common measurement units, stable field names and order, a chosen document structure and layout, and a standard output file type. Search, product views and sales graphs make that standardized information useful; they are supporting features, not the main purpose.

[Source and Actions](https://github.com/JasonStys/business-knowledge-workbench) · [Downloads](https://github.com/JasonStys/business-knowledge-workbench/releases/latest) · [Contact Jason on LinkedIn](https://www.linkedin.com/in/jason-stys-31b30b351/)

Version **1.2.0** adds owner-controlled output standards, draft previews, schema mapping, version history/restoration, current-standard copies and standardized report downloads. Login, independent vault encryption and the existing navigation-readiness regression are preserved. See [standards guide](docs/standards.md), [requirements review](docs/requirements-review-v1.2.md) and [validation](docs/validation-v1.2.md).

![Installed private account website with blank credential fields](docs/screenshots/accounts.png)

## What “standardize” means

Suppose supplier A sends a CSV field `length` containing `4.25 in`, supplier B
sends JSON with `Width: "8.2 cm"`, and a technician sends a DOCX table. The owner
defines canonical fields `item, width`, their displayed headings, order and a
millimeter target. Recognized tables then share the same schema and measurements
(`107.95 mm`, `82 mm`), even though the source files differ. Optional fields have
explicit empty cells; missing required fields, incompatible dimensions and
ambiguous duplicate headers are rejected. Extra columns are preserved and flagged
or explicitly rejected, never silently discarded.

For documents, the selected standard controls section order and headings, font,
heading color, Letter/A4 paper, portrait/landscape orientation and preferred
HTML/JSON/Markdown/CSV/DOCX/PDF delivery. An optional policy restricts document and
report exports to that chosen type. Every conversion still goes through canonical
HTML first. Original source bytes, pre-normalization blocks, warnings, the settings
snapshot, revision and standard digest remain available for comparison.

This is **normalization, not invention**: the app does not guess units on arbitrary
bare numbers, equate unrelated fields automatically, translate currencies or
certify that extracted facts are true. A declared table field may specify a source
unit for bare numbers. Graphs, images and equations can be retained without their
meaning being understood. See [format and fidelity limits](docs/formats.md).

## Define your business standard

1. Unlock your own private account and open **Configuration studio**.
2. Set target units, document section order/headings, standard name, print layout
   and default export type. Configure optional table keys, aliases and required
   fields; the measurement-table example is an editable starting point.
3. Use **Preview draft standard** with a small CSV sample. This does not publish
   anything, call an AI provider or alter stored documents.
4. **Save validated configuration** publishes a new revision. A stale editor gets
   a conflict instead of overwriting someone else's newer revision.
5. Import supported files or combine authorized documents. Open the result and
   choose **Download standard…**. Reports also have a standard-format download.
6. For an older document, choose **Create current-standard copy**. Originals and
   sales remain unchanged. **Restore as new revision** recovers a saved standard
   without rewriting its history or prior documents.

![Owner-controlled output standard in a disposable fictional business account](docs/screenshots/standards.png)

The screenshot shows a published PDF/A4/landscape standard and its saved schema;
no real account credentials, documents or provider keys are included.

Authority is enforced on the server, not just by hiding a button. In the installed
private edition, the signed-in, vault-unlocked account owner is the standards
authority for their own data. There are **no shared-business invitations or
delegated coworker roles** yet. Customer/employee screens are own-account previews;
in the separate legacy role demo, only the database-authenticated administrator
may preview, publish, read history or restore standards. A client-supplied role
header cannot promote a legacy employee or customer. A responsible standards
manager would need a trusted shared-team authorization deployment, not a UI toggle.

## Install and start

Download a release for your OS, verify its SHA-256 record and launch the app. The Windows per-user setup is one click; a portable ZIP is also provided. macOS arm64 and Linux x64 packages are available. Native packages include Python, the document service and the UI—no terminal setup is needed for normal use. Builds are **unsigned / not notarized**; no claim of store approval or universal hardware support.

Choose **Open local website** from the desktop menu to use the same app in a browser. The service binds only `127.0.0.1` on an automatically selected port. There is no public hosted website, paid hosting, telemetry or Jason-operated account server. A phone cannot connect to another device's loopback address; this release has responsive web layouts, not native mobile installers.

Create an alias and login password, privately save the once-shown login recovery code, then choose a **different vault phrase**. Forgotten vault phrases cannot be recovered or reset by Jason. See [private accounts and user guide](docs/private-accounts.md).

## Main features

- Fifteen supported extensions: text, Markdown, sanitized HTML, CSV/TSV, JSON, XML, DOCX, XLSX, PDF and raster images. Original evidence, semantic blocks, extraction warnings and hashes are retained.
- Canonical **HTML first**, then HTML, JSON, Markdown, CSV tables, DOCX or PDF export. Graphs/images are preserved where supported, not universally understood; read the [format limits](docs/formats.md).
- Decimal-based measurement normalization with dimension validation; `4.25 in → 107.95 mm`, `104 F → 40 C`. Configuration revisions preserve provenance.
- Named, data-only standards with field aliases/order, optional/required columns, explicit measurement dimensions, draft previews, immutable revision history and controlled export types. No executable user templates or arbitrary CSS.
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

[Current validation](docs/validation-v1.2.md), [original validation](docs/validation-v1.1.md), [standards test plan](docs/standards.md#verification) and [private API](docs/private-api.md) distinguish actual conversions/browser/native tests from provider mocks and unsupported deployments. CI retains logs; large Actions artifacts are **opt-in** through `KBW_UPLOAD_CI_ARTIFACTS=true`. Tested downloads go to Releases instead of consuming Actions artifact quota.

## File responsibilities and language choices

| Area | Responsibility |
| --- | --- |
| `web/main.ts`, `types.ts`, `style.css`, `index.html` | Typed document/product/reporting views, accessible HTML, responsive styling and escaped rendering. |
| `web/private.ts` | Account forms, browser key derivation, help, own AI settings, consent and human-activity signals. |
| `server/accounts.py`, `permissions.py`, `vault.py` | Local authentication/session/recovery hashes, dedicated OS-user permissions and streamed authenticated snapshots. |
| `server/private_api.py`, `private_workspace.py`, `private_cli.py` | Exact-loopback boundary, account-isolated document engine, serial lifecycle/idle recovery and local launch. |
| `server/app.py`, `models.py`, `store.py`, `schema.sql` | Preserved business API, validation, relational integrity, scoped searches and synthetic seeding. |
| `server/conversion.py`, `worker.py`, `units.py` | Supported rich-format parsers, bounded child conversion and exact normalization. |
| `server/standards.py`, `web/standards.ts` | Deterministic field/schema mapping, standard fingerprints and safe typed editor controls. |
| `server/exports.py`, `analytics.py`, `ai.py` | HTML-derived exports, explainable reporting and read-only model contracts. |
| `desktop/main.cjs` | Electron shell with an owned frozen service, denied external navigation/popups and graceful sealing. |
| `scripts/` | Frozen entry, licenses/checksums, fixture/benchmark and exact line/file inventories. |
| `tests/`, `playwright*.config.ts` | Real parser/API/crypto/role regressions, browser journeys and native packaged-app tests. |
| `public/`, `examples/` | Shell-only legacy PWA assets and clearly fictional sample evidence; no user data. |
| `.github/workflows/`, root configuration | Reproducible dependency/build/CI/package/release gates and optional legacy container. |
| `docs/` | Usage, limits, architecture, contracts, validation/release evidence and per-file/source maps. |

Python uses its mature document ecosystem, TypeScript provides typed browser interactions, SQL provides transactional business persistence, HTML/CSS keep outputs inspectable, and JavaScript powers the isolated desktop shell. [The complete file catalog](docs/file-catalog.md) summarizes each tracked file; [the generated code index](docs/code-index.md) maps every authored code file's functions/classes/variables to exact lines. Regenerate inventories after source edits.
