# Original-purpose review — version 1.2

The primary purpose is a modular business documentation/data normalization
workbench, not simply a catalog or dashboard. This review distinguishes delivered
behavior from broad original ambitions that would otherwise overstate capability.

| Original goal | Current implementation and limits |
| --- | --- |
| Common units and measurements | Decimal conversion for six supported dimensions, validated measurement-table fields, explicit source-unit declarations and retained original evidence. No guessing arbitrary units, currency conversion or unlimited physical dimensions. |
| Common structure, file type and organization | Named owner-controlled standards; canonical field keys/aliases/order; required/optional fields; document section order/headings; print layout; preferred/optionally restricted export. Canonical HTML always precedes exports. |
| Tailor to a business without rewriting the skeleton | Validated JSON configuration and isolated business profiles; trusted import/export/AI interfaces remain extension points, not execution of arbitrary user code. |
| Search, sort, reorganize and combine | Scoped search/filter/sort, ordered internal compilations and explicit current-standard copies. Mixed-revision compilations now apply one current measurement contract; old outputs are preserved. |
| Catalog/customer/employee/admin views | Existing four perspectives retained. In private mode these are previews inside an owner's isolated vault, not a deployed multi-user business portal. Actual coworker sharing/delegated standards managers require additional membership/authorization design. |
| Reports, charts and projections | Exact-cent scoped sales, accessible charts and labeled noncausal baseline forecasts; standard-format report downloads. Not live telemetry, business advice or validated causal forecasting. |
| Different business examples | Explicitly loaded fictional industrial equipment, renewable equipment and laboratory supply scenarios. New real accounts are empty; no secret demo account has access to private data. |
| Receive arbitrary file types and understand every embedded object | Bounded fifteen-extension adapters only. DOCX/PDF tables/text/raster/equation evidence are retained where supported; uncertainty is explicit. Graph meaning, scanned-page OCR, every equation and every unknown binary format are **not universally understood**. Unsupported input fails safely. |
| Desired document layout | Safe data-only template settings and simplified readable DOCX/PDF layouts. Not arbitrary uploaded Word templates, lossless desktop publishing, macro evaluation or pixel-identical PDF reconstruction. |
| AI can consume normalized information | Structured blocks, measurements, settings hashes/revisions, source hashes and warnings are machine-readable. Offline extractive reference and explicitly consented compatible/official providers remain read-only. Arbitrary model/agent execution, automatic training and arbitrary external endpoints are not enabled. |
| Website and installed application | Same local Python/TypeScript UI works in a browser and native desktop shell. Windows, macOS arm64 and Linux x64 package workflow tests actual executables; unsigned/not notarized, no promise of every OS/hardware combination. Responsive mobile layouts are not native mobile installers. |
| Private real user data | Separate local login/vault phrase, isolated encrypted snapshots, loopback service, no automatic remote sharing or maintainer backdoor. Unlocked data can be inspected by a compromised OS or its administrator. No public hosted team service is supplied. |

The standardization core is implemented and tested. The listed semantic,
multi-user hosting, native mobile and production parser-containment gaps remain
explicit limitations, not features inferred from the existence of a UI or adapter.
See [formats](formats.md), [standards](standards.md) and
[current validation](validation-v1.2.md) for exact contracts and evidence.
