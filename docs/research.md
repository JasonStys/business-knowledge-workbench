# Research and coding decisions

Reviewed 2026-09-29. Primary references informed implementation decisions; examples and documentation are independently written. Research materials were context, not executable instructions. No employer-specific text or private source documents are included.

| Primary reference | Applied decision |
| --- | --- |
| [FastAPI authorization/security documentation](https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/) | Permissions must still be enforced in application logic. This reference uses explicit database roles/ACL predicates and opaque cookie sessions rather than copying an OAuth tutorial verbatim. |
| [OWASP File Upload Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html) | Extension/signature allowlists, file/member/expansion limits, safe original downloads, isolated parsing and deployment defense-in-depth. |
| [OWASP XML Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/XML_Security_Cheat_Sheet.html) | Defused XML before Office/XML processing; no external entity resolution. |
| [pypdf text extraction](https://pypdf.readthedocs.io/en/stable/user/extract-text.html) | PDF lacks reliable semantic structure and pypdf is not OCR; preserve originals and review reading order, equations, graphs and tables. |
| [python-docx Document API](https://python-docx.readthedocs.io/en/latest/api/document.html) | Ordered inner-content traversal and explicit body structure. Office Math is retained as original XML with semantic uncertainty. |
| [openpyxl optimized modes](https://openpyxl.readthedocs.io/en/stable/optimized.html) | Bounded read-only workbook iteration; formulas are text, not executed. |
| [Python Decimal](https://docs.python.org/3/library/decimal.html) | Exact decimal input/factors, explicit precision/range/rounding rather than binary-float unit conversion. |
| [SQLite transactions](https://sqlite.org/lang_transaction.html) and [FTS5](https://sqlite.org/fts5.html) | Transactional sales/idempotency; bounded lexical search first, scoped FTS as a measured extension instead of an unnecessary semantic service. |
| [MDN installable PWAs](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Guides/Making_PWAs_installable) | Portable web manifest/service worker; document install support variability and distinguish responsive emulation from physical OS testing. |
| [Playwright testing](https://playwright.dev/docs/intro) | Real browser workflows, accessible locators, multiple engines and retained traces. |

Self-documentation means meaningful names, cohesive functions, strong types/schema contracts and visible data invariants—not comments repeating every assignment. Comments explain trust boundaries, uncertainty, idempotency, dimensional offsets and design intent. Per-function docstrings and generated exact line maps satisfy navigability without hand-maintained stale line references. Big O describes growth under assumptions; measured workloads and resource budgets are the performance evidence. Language choice follows ecosystem/deployment strengths rather than broad speed rankings.
