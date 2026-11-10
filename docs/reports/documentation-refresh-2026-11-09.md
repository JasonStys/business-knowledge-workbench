# Documentation refresh — 2026-11-09

By Jason Stys.

This documentation-only edition describes source `a25887ac0e54f2afbe0e21e597c67b606890e8ad`. It does not change application behavior, accounts, private data, installers or published releases.

## Published editions and completed review

| File | Bytes | SHA-256 | Reviewed scope |
| --- | ---: | --- | --- |
| [project-guide.docx](project-guide.docx) | 154583 | `6666cdd2bef1cb4097133eba9b5c2adb8ef6ff2fc59527b331b11d32f6d6c5c7` | 7 pages, each viewed individually |
| [validation-review.docx](validation-review.docx) | 42385 | `73370ebad9ee232de7fe6697510f724e5d8f674a8ab858f6ae62fc669c74e764` | 3 pages, each viewed individually |
| [validation-evidence.xlsx](validation-evidence.xlsx) | 7466 | `6f1f03ff509e2a23861e4a23c251b61f6067c7692afe7c6df6cfaee657bdf64d` | Both tab previews; two actual Excel Tables/autoFilters; four formulas; failure-change/restore recalculation and zero formula errors |

Word review checked plain black titles, readable pagination, whole table rows, source references, practical limits and absence of clipping or overflow. Render receipts were matched to the current DOCX digest before approval. Workbook review inspected both tab previews and actual exported Table/autoFilter elements; recalculated success/failure summaries were compared independently with workflow metadata. Static previews do not draw Excel dropdown arrows; the exported workbook contains the actual filters.

## Evidence and change boundary

- Functional baseline: `a25887ac0e54f2afbe0e21e597c67b606890e8ad`.
- Workflow observation: `2026-11-10T05:25:40.628667+00:00`; exact run URLs and source identities remain in [publications.json](publications.json).
- Local document-package validation verifies exact copied bytes, Office ZIP integrity, approved page/tab identities and internal documentation links. Repository-specific documentation and source-policy commands are run separately and recorded in the integration handoff.
- Source/index metadata is regenerated using the repository’s existing tools. Existing privacy, security, coverage and workflow gates are retained.
- PR and later main workflows must pass independently. This record does not claim future or unrun integration CI success.

## Interpretation

The Word files document the cited source; dated source reports retain their original execution scope. A passing workflow is distinct from completed analysis with zero findings, and neither establishes production suitability. The Excel source inventory is not a per-test execution report. Checksums identify exact bytes, not a signature or publisher attestation.

Use the [handbook](../handbook.md) to choose usage, design, security and test documentation. Keep editable Markdown and reviewed editions together; do not replace historical measurements with undated claims.

## Integration-local checks

Observed at `2026-11-10T07:33:46.520053+00:00` on Windows in this repository’s isolated locked development environment. Commands below use its activated Python environment. The documentation source baseline remains the immutable revision above; these checks validate this documentation integration locally.

| Command | Observed result |
| --- | --- |
| `python scripts/code_index.py` | Passed, exit 0. |
| `python scripts/file_catalog.py` | Passed, exit 0. |
| `python scripts/code_index.py --check` | Passed, exit 0. |
| `python scripts/file_catalog.py --check` | Passed, exit 0. |
| `python -m ruff check server scripts tests/python` | Passed, exit 0. |
| `python -m ruff format --check server scripts tests/python` | Passed, exit 0. |
| `python -m pytest -q` | Passed, exit 0. |

The independent publication audit also matched every copied Office file to its approved SHA-256, checked ZIP package integrity and current page/tab approvals, compared immutable workflow/source metadata, and resolved every local handbook/report link within the repository. Hosted PR/main, browser, platform and container jobs remain separate required checks; they are not inferred from these local results.

The existing Python suite was executed against disposable test state. Only reviewed Office assets, documentation, generated navigation and known catalog descriptions change; private stores, accounts, application behavior and published downloads are preserved.
