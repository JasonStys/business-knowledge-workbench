# Architecture and ADR 001: portable, HTML-centered business knowledge

Status: accepted for reference application v1. Audience: developers adapting a small business workspace. Revisit for high-volume ingestion, multi-customer inventory relationships, SSO requirements or native store distribution.

## Requirements and assumptions

One small service handles bounded sources (4 MiB), 200 searchable documents per organization and modest concurrent use. Documents, sales and configuration persist. Visitors see public records; customers see their account evidence and inventory; staff see the active business; administrators change validated parameters. No role from browser state is trusted. Tenant/customer attributes come from stored user records.

The reference schema assigns each product/inventory entry to one account group. Public catalogs are broader than customer inventory. A many-to-many product/customer assignment table is the appropriate extension for a large supplier; do not reinterpret this example as a complete ERP.

```text
Responsive TypeScript UI / installed PWA
             │ same-origin HTTPS, session cookie, CSRF token
             ▼
Python API ── authorization ── SQLite + validated configuration + audit
    │                                 ▲
    ├─ bounded source → isolated parser → semantic blocks → canonical HTML
    │                                       │                 ├─ previews
    │                                       │                 └─ six exports
    ├─ mapped tables → atomic sales rows → scoped reports / baseline forecast
    └─ ACL-filtered JSON context → read-only model adapter → checked citations
```

Every file conversion crosses the HTML stage. Structured JSON keeps both the HTML representation and semantic blocks. Derived outputs never replace original evidence. Sources are BLOBs, not user-named filesystem paths. HTML from users is sanitized; textual values are escaped. Previews use scriptless sandbox frames. Original sources download only as octet-stream attachments.

## Decisions and alternatives

| Option | Complexity / cost | Scale / familiarity | Trade-off |
| --- | --- | --- | --- |
| TypeScript UI + Python API + SQL (chosen) | Small dependency boundary; one same-origin process after build | Browser standards and mature Python document ecosystem | Two build environments; runtime schemas are still essential. |
| JavaScript-only extraction/API | One language/runtime | Familiar web stack | Rich office/PDF and analytical adapters would require additional external converters. |
| Microservices + queues + PostgreSQL/object storage | Higher operational cost | Better ingestion/tenant scale | Excess complexity for bounded local examples; appropriate next boundary under load. |
| SQLite + BLOB sources (chosen) | No external service credentials or billing | Small single-instance deployment | Serialized writes and growing database backups; not intended for large distributed ingestion. |
| Static-only browser website | Easiest hosting | Excellent public catalog delivery | Cannot enforce private ACLs or protect model secrets; rejected for this application. |
| PWA (chosen) | One responsive implementation | Desktop/mobile browsers | Installation varies by platform; not equivalent to signed native packages. |
| Native wrappers per OS | Multiple toolchains/signing/store cost | Native OS integration | Useful if offline private storage or device APIs become requirements. |

## Components and change boundaries

`models.py` defines validated parameters rather than arbitrary templates/code. `conversion.py` exposes `extract`, `ingest` and `render_document`; add trusted importers that emit the same block schema. `exports.py` accepts canonical HTML. `ai.py` defines a narrow callable contract; hosted/local endpoints and factory code are operator-owned settings. `analytics.py` is deliberately independent of AI: changing models cannot change reporting arithmetic.

Configuration includes title, profile ID, account labels, target units, ordered document sections, mapped sales column names, forecast toggle and AI opt-in. Revision checks reject stale admin writes. Existing conversion revisions are immutable. Reimport applies new standards. Compilations retain per-source measurement provenance and may mix historical unit targets: reimport sources under one profile before compiling; do not assume merging changes their numerical meaning.

## Data integrity and complexity

SQL foreign keys, checks and transactions guard relationships and nonnegative values. Sales are exact integer cents, never currency-converted. Measurements use Decimal with six-decimal output rounding, preserve original spelling and reject incompatible dimensions or temperatures below absolute zero. Explicit recognized units are converted; ambiguous prose, bare numbers and equation operands are not guessed.

Search is an ACL-filtered lexical substring scan: O(n·t) over bounded documents/text, with O(k log k) sorting of selected results in SQLite. Workspace/scope indexes narrow selection; no semantic index can accidentally bypass ACLs. The small cap is intentional. Add FTS5 and scoped ingestion/chunk indexes when profiling shows a need. Parsing/normalization is roughly O(input text + cells); document-specific parsers have complex internal behavior, so limits and a 25-second process timeout matter more than a simplistic Big O claim. Monthly SQL aggregation is O(sales rows); OLS fitting is O(months) time/space. The benchmark records actual runtime, workload and generous CI budgets rather than claiming language-wide speed rankings.

## Failure and security model

Unsupported/corrupt/over-budget sources return 4xx, leaving no partial sales records. Two conversion slots prevent unbounded process creation per service process. Archive expansion, table/image/page/text budgets, UTF-8 checks and defused XML protect import boundaries; container limits are additional defenses. Python subprocess isolation/timeouts are not a complete operating-system sandbox, especially on Windows. Untrusted public ingestion needs dedicated parser containers, antivirus/CDR and a hardened egress policy.

Session identifiers are opaque, hashed in the database, expire after one hour and use HttpOnly/SameSite=Strict cookies. Mutations require an independently stored CSRF token. Same-origin checks reject cross-origin writes. Read-only API responses are never service-worker cached. Customer/workspace filters are enforced before retrieval, direct-ID export and model context creation.

AI gets untrusted scoped source text, no SQL handles, credentials or action tools. The system instruction rejects source instructions, but prompt-injection resistance is not guaranteed. Output/citations are bounded and checked; every answer remains unverified. A legitimate model can still hallucinate while citing a valid source. Human review and optional provider/data-transfer approval remain necessary.

## Consequences and action items

Keep the reference small and reproducible. Move sources to object storage, parsing to a resource-isolated job queue, sales/product assignments to business-specific schemas and auth to an OIDC provider for production. Preserve ACLs, source hashes and HTML-first contracts across those moves. Add measurements only with domain-reviewed units, ranges and offset semantics. Use a fresh database for clean business provisioning rather than promoting a demo database.
