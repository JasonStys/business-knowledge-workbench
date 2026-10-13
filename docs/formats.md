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
| Native Windows x64 | Per-user setup and portable ZIP with bundled service | Real frozen-service and packaged-executable document journeys in CI; released ZIP independently tested on this PC. Unsigned. |
| Native macOS arm64 | DMG and portable archive with bundled service | Real frozen-service and packaged-executable document journeys on macOS CI. Not notarized or developer-identity signed. |
| Native Linux x64 | AppImage and portable archive with bundled service | Real frozen-service and packaged-executable document journeys on Linux CI. No universal distribution/architecture claim. |
| Installed legacy desktop/mobile PWA | Separate demonstration manifest/shell worker | Manifest/assets/offline/privacy checks automated. Private mode does not register this worker; no native phone package. |
| Offline private documents | Local Python/native service works without an external network | Own trusted local service must be running. AI reference is offline; external/local model connections are opt-in. No private browser caching. |
| Native mobile/app stores | Not generated | Physical phone testing, store approval, signing/notarization and remote shared hosting remain separate work. |

The private account edition binds only to the same device's loopback address, not a public HTTPS host or another phone. Legacy PWA support is separate; browser installation instructions evolve—see [MDN's installation guidance](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Guides/Installing). This repository does not claim physical installation on every OS/device. See [private accounts](private-accounts.md) and [current validation](validation-v1.1.md).
