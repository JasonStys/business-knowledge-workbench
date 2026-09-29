# Runbook, installation and release checklist

## Local demo versus real business setup

`KB_DEMO=1` explicitly seeds synthetic accounts/products/docs/sales. Default normal mode does not create demo users or sample sales. A fresh database is the clean boundary; turning off demo mode does not delete previously seeded accounts. Never promote an existing demo database to real use.

```bash
python -m server.manage --db data/business.sqlite workspace my-business "My business"
python -m server.manage --db data/business.sqlite user my-business owner admin
```

Password entry is interactive, requires confirmation and at least 12 characters, and stores a salted scrypt hash. Set `KB_DB=data/business.sqlite` and `KB_DEMO=0`. Admin UI can add account labels; provision customers with `--customer configured-id`. An operator provisions employee accounts similarly. Password reset, account deactivation, SSO, retention/deletion and automated secret rotation are production extensions, not hidden features.

## Deployment settings

| Setting | Meaning |
| --- | --- |
| `KB_DB` | Server-owned SQLite path. Default `data/workbench.sqlite`; never request-provided. |
| `KB_DEMO` | `1` enables invented reference data/accounts; never use for real records. |
| `KB_ORIGIN` | Exact public origin used for mutation checks, e.g. `https://knowledge.example.com`. |
| `KB_SECURE_COOKIE` | Normal mode defaults to `1`; demo mode defaults to `0`. Require `1` behind HTTPS; `0` is only for local HTTP development. |
| `KB_AI_ENDPOINT`, `KB_AI_MODEL`, `KB_AI_KEY` | Operator-owned model endpoint/name/secret; never committed or returned to browser. |
| `KB_AI_FACTORY` | Trusted Python `module:factory`; takes precedence over compatible HTTP adapter. |
| `KB_LOGIN_LIMIT` | Default 10 login attempts/minute/address; bounded 10–100. Browser tests use 100. |

Run a single API worker for this small reference. Per-process limits are not shared across multiple instances. Reverse proxies must enforce request size, concurrency, rate limits, trusted forwarded headers and timeouts. TLS terminates at a reviewed proxy; serve app/API on the same origin. No wildcard CORS is configured. Use a private volume, least-privilege service identity, reviewed model egress and monitored backups. Secrets are deployment inputs, not admin-editable parameters.

The Docker image builds frontend assets and serves them with Python, using UID 10001. Compose binds only local loopback, drops capabilities, uses read-only root plus data volume and bounded `/tmp`, and applies memory/CPU/PID budgets. It is a local demo configuration, not a ready public production deployment. Container CI actually builds, starts and probes the service; local Docker testing requires an available daemon.

## PWA installation

Use HTTPS remotely or loopback locally. In browsers offering installation, choose **Install app** / **Add to Home Screen**. The manifest requests standalone display with desktop/mobile icons. Safari, Chromium and Firefox have different installation affordances; some browsers run the website without installation. No signed native binaries or store submissions are implied. Private API data is not service-worker cached. An installed offline app shows a connection-required screen, not stale customer evidence.

## Backup and recovery

```bash
python -m server.manage --db data/business.sqlite backup backups/business-2026-09-29.sqlite
```

SQLite's backup API creates a consistent new file; the command refuses to overwrite a destination or the live DB. Protect backups as sensitive data, including source BLOBs, sessions, password hashes and audit records. Test restore into a **new** path: stop the service, point `KB_DB` at a copy, start the matching source version and probe health plus authorized document/report flows. Do not overwrite the only working database. Schema v1 initialization is idempotent and rejects unknown versions; migrations require an explicit tested upgrade/rollback plan.

## Troubleshooting

401: session expired or invalid credentials; reauthenticate. 403: role, origin or CSRF; verify deployment origin and secure-cookie/TLS settings rather than disabling checks. 409: reload stale configuration, enable AI deliberately, use a distinct product ID, or review an already applied sales source. 413/415/422: inspect the format matrix and source, correct errors, or implement a tested adapter. Never retry unsupported files indefinitely. 429 conversion: wait for current workers and inspect load; do not increase limits without memory measurements. 502 AI: inspect provider support/config privately, never expose provider exceptions/keys to customers. Uncertain extraction: compare original file and semantic blocks; use a reviewed OCR/vision adapter where needed.

## Release checklist

- Build, lint, type checks, Python coverage, all browser workflows, dependency scans and code-index freshness pass on the exact release commit.
- Check GitHub Actions **Validate workbench** and **CodeQL**, not only local test output. Inspect code-scanning alerts separately from successful scanner execution.
- Verify product search, both customer scopes, employee import/report/merge, admin config revision and explicit AI opt-in. Check direct-ID cross-tenant denials.
- Confirm container health and non-root execution; keep latest reports as Actions artifacts.
- Record format/AI/native-device limitations. Fake model tests are not evidence of live provider quality.
- Before real deployment: review security, identity, TLS/cookies, source handling/isolation, egress/consent, persistence quotas, data retention, recovery and monitoring with the organization.

Rollback triggers: critical account-boundary failure, corrupt exports, data multiplication, unexpectedly missing provenance, repeated parser timeouts or an incompatible schema. Stop imports/model transfers; restore the previous reviewed app image/config with a compatible new backup path. Existing original sources remain available for reprocessing. This portfolio release does not claim a monitored public production deployment.
