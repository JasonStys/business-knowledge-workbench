# Supported formats, fidelity and platform matrix

No software can promise to interpret every arbitrary file and all its semantics. This application identifies supported extensions, checks payload structure, and retains uncertainty. Unsupported formats return 415. Legacy `.doc`, `.xls`, encrypted PDFs, archives, macros, arbitrary binaries and executable plugins are not importable sources.

| Input | Extracted / retained | Explicit limits |
| --- | --- | --- |
| TXT | UTF-8 paragraphs, explicit measurements | No arbitrary legacy encodings or binary text; 200,000 characters. |
| MD | CommonMark headings, lists and prose | Raw embedded HTML is disabled; pipe tables and other unsupported Markdown extensions remain plain text. |
| HTML/HTM | Sanitized headings, prose, tables and HTTPS links | Scripts/styles/objects/remote assets removed. Original remains downloadable. |
| CSV/TSV | Ordered table strings and explicit unit cells | 2,000 rows, 40 columns; formulas are not executed. |
| JSON | Object text or an array-of-records table | Valid JSON only; nonfinite numeric constants rejected. Nested structures remain text. |
| XML | Defused text extraction and retained original tree | No DTD/entity resolution; canonical representation is text, not an XML round-trip. |
| DOCX | Ordered body paragraphs/tables, inline raster figures, Office Math source XML/text | Complex/nested objects, tracked edits, headers/footers, equations and layout require original-source review. |
| XLSX | Up to 12 sheets of cell strings, formula spelling | No formula execution, macro support or semantic chart interpretation; images/charts remain in source. |
| PDF | Text layers, detected ruled tables, embedded raster figures | At most 30 pages; reading order, graph axes, equations and table boundaries are uncertain. No automatic OCR. Scans require OCR/vision adapters. Vector graphics remain in source. |
| PNG/JPG/JPEG/WebP | Bounded re-encoded PNG figure with review status | At most 8 million pixels; image meaning is unknown until explicit vision analysis and review. |

Office ZIPs: at most 300 members, 16 MiB total expansion, 8 MiB per member, compression ratio ≤200; reject suspicious paths/encryption and XML entities. PDF page content streams are checked, but decompression itself may allocate memory before that check—resource-limited parser hosting is necessary for untrusted workloads. Each source is at most 4 MiB; the worker deadline is 25 seconds.

## HTML-first outputs

The canonical HTML is generated before any output adapter. HTML includes document sections, tables, normalized values, figures and provenance. JSON includes semantic blocks and original equation XML. Markdown is a readable text-oriented derivative. CSV exports tables with spreadsheet-formula injection protection. DOCX/PDF exports are **simplified readable layouts**, not byte-identical or pixel-identical replicas; wide PDF tables split into column groups. Base PDF fonts do not guarantee full Unicode typography: use canonical HTML/JSON as the multilingual authority, or add reviewed embedded fonts. Graph/equation meaning is not reconstructed by the exporter.

Source → HTML and HTML → target paths are recorded in JSON provenance. Original files remain authoritative when layout or semantics matter. Source hashes demonstrate byte identity, not trustworthy business facts. Review labels (`extracted`, `needs-review`, `unverified`) are not approval signatures.

Unit tokens are not complete natural-language understanding. An `in` token followed by another word (e.g. `2 in stock`) is kept unchanged to avoid mistaking a preposition for inches. Missing/ambiguous units require domain review rather than automatic guessing.

## App portability

| Surface | Implementation | Verification boundary |
| --- | --- | --- |
| Windows/Linux/macOS browsers | Standards-based responsive TypeScript/HTML/CSS | Automated Chromium, Firefox and WebKit engines; server matrix on Windows and Linux. |
| Android/iOS mobile browser layouts | Responsive interface and web manifest | Mobile Chromium viewport/touch emulation, not physical phone testing. |
| Installed desktop/mobile app | PWA, standalone display, PNG icons, HTTPS/localhost service worker | Manifest/assets/offline/privacy checks automated. Installation UI varies by browser/platform. |
| Offline | Connection-required screen | No confidential document/sales/API caching. This is not an offline private-data application. |
| Native stores/binaries | Not generated | Signing, OS APIs and app-store distribution need a separate native wrapper/release pipeline. |

Use HTTPS for remote installation. Browser support and installation instructions evolve; consult [MDN's installation guidance](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Guides/Installing). This repository does not claim physical installation was tested on every operating system.
