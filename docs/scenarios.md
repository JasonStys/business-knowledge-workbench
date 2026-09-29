# Synthetic business scenarios and acceptance walkthroughs

All names, accounts, identifiers, specifications and commercial values are fictional. They demonstrate software behavior; they are not manufacturer specifications, engineering advice, forecasts for a real company, or confidential customer data.

## Meridian Controls: industrial automation supplier

A pump integrator buys an edge controller and isolated remote I/O while another customer buys a DIN-rail power supply. Employees manage specification manuals, commissioning packs, service evidence and sales. Mixed supplier dimensions use inches/centimeters; the default target is millimeters. Voltage may be expressed in V or mV. Precise model IDs must remain searchable.

Inputs: `commissioning-pack.docx` (ordered table, raster throughput graph and Office Math equation), `controller-performance.pdf` (text, ruled table, figure and formula), `industrial-sales.csv` (three mapped January rows), `mixed-measurements.csv`, `service-record.xml`, `installation-note.md` and `throughput.png`.

Expected: `4.25 in → 107.95 mm`; `8.2 cm → 82 mm`. North portal shows its controller/I/O service records but not south's supply service record or internal operations notes. Public product overviews remain public. Importing sales adds 4,231,300 cents exactly once. Compiling public/private sources always creates an internal pack. PDF/DOCX graph and equation fidelity warnings remain visible; model vision is unverified and requires explicit opt-in.

## Solstice Energy Supply: renewable equipment distributor

A commercial installer compares panel, storage and inverter products across supplier documents. Sources use centimeters/inches, pounds/kilograms and Wh/kWh. Employees track shipment/customer inventory and commercial activity; customers see their assigned equipment. The scenario is deliberately not an energy-production forecasting model.

Input: `renewable-specifications.xlsx`, including `113.4 cm`, `48.5 lb`, `104 F`, plus seeded customer documentation and 12 months of synthetic sales.

Expected: default normalization gives 1134 mm, 21.99947 kg and 40 C. An admin can choose energy `kWh` for future imports. Formula text is never executed. Workbook graph/macro semantics are not guessed. Customer, organization and exact-cent reporting boundaries remain identical to the industrial profile.

## Atlas Laboratory Supply: equipment and service distributor

A materials laboratory owns a precision balance and thermal chamber; another customer uses a pressure gauge. Staff consolidate calibration records, equipment dimensions and service information. This is a nonclinical fictional scenario; no medical or regulatory decisions are automated.

Input: `laboratory-record.json` plus seeded product/service/internal documents. Metadata includes mass, length, temperature and pressure, and the provenance contract stays portable for later analytical processing.

Expected: width 22 cm becomes 220 mm; thermal setting 104 F becomes 40 C. Incompatible conversions such as kilograms to millimeters fail with a validation error. The report is customer-scoped, its chart has a numerical table, and its optional projection is labeled an OLS baseline—not a validated causal model.

## Clean custom business

Create a new profile with the operator CLI, provision a trusted admin, configure customer labels and sales aliases, then create a product from Business workspace. This path proves the reference scenarios are not hardcoded as the only allowable tenant IDs. Start with an empty database to avoid carrying demo accounts into a real deployment.

Fixture builders: `scripts/fixtures.py` generates PDF/raster/CSV/XLSX/JSON/XML/Markdown and PWA icons; `scripts/docx-fixture.mjs` generates the rich DOCX with explicit Letter page/table widths. Binary fixtures are committed so tests do not depend on document-authoring tools at runtime. ZIP timestamps/producer metadata may change on regeneration; byte hashes identify that particular source, not a semantic version.
