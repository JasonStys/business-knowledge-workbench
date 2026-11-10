# Business Knowledge Workbench handbook

By Jason Stys.

Standardize supported business documents and tabular data into a consistent structure, selected measurement units and export format. Authorized standards owners define the active fields and presentation; permitted readers can investigate the standardized library and download the results. Conversion support remains specific to the documented adapters.

Search standardized numeric table values with unit-aware ranges and same-cell correlation; download authorized bounded document bundles with checksummed manifests and saved standards. Fixed scientific notation normalization.

Makes standardized business records easier to investigate and hand off without mixing units or bypassing document access.

## Read the documentation

| Edition | Audience and contents |
| --- | --- |
| [project-guide.docx](reports/project-guide.docx) | User and developer guide: purpose, current usage, design, boundaries and source references. |
| [validation-review.docx](reports/validation-review.docx) | Reviewer edition: exact tested baseline, observed workflows, dated local results and remaining limits. |
| [validation-evidence.xlsx](reports/validation-evidence.xlsx) | Two filterable Excel Tables for observed workflows and test-source inventory, with recalculating outcome formulas. |

The editable Markdown remains the maintenance source. The Word files are readable editions, and the workbook is an evidence index rather than a test runner. See [publication identities and review](reports/publications.json) and the [documentation refresh record](reports/documentation-refresh-2026-11-09.md).

## Current usage and help

[README quick start](../README.md) is the entry point. Use the project-specific guides below before changing inputs, operating modes or deployment assumptions.

### Usage and operations

- [operations](operations.md)
- [release checklist](release-checklist.md)
- [releases/v1.1.0](releases/v1.1.0.md)
- [releases/v1.1.1](releases/v1.1.1.md)
- [releases/v1.2.0](releases/v1.2.0.md)
- [releases/v1.3.0](releases/v1.3.0.md)
- [releases/v1.4.0](releases/v1.4.0.md)
- [requirements review v1.2](requirements-review-v1.2.md)

### Design and contracts

- [adr private local](adr-private-local.md)
- [api](api.md)
- [architecture](architecture.md)
- [private api](private-api.md)
- [research](research.md)

### Security and validation

- [test plan v1.1](test-plan-v1.1.md)
- [validation v1.1](validation-v1.1.md)
- [validation v1.2](validation-v1.2.md)
- [validation v1.3](validation-v1.3.md)
- [validation](validation.md)

## Historical results and reproduction

The reviewed source is [`a25887ac0e54f2afbe0e21e597c67b606890e8ad`](https://github.com/JasonStys/business-knowledge-workbench/tree/a25887ac0e54f2afbe0e21e597c67b606890e8ad). The observed functional workflow baseline is `a25887ac0e54f2afbe0e21e597c67b606890e8ad`; those observations are recorded at `2026-11-10T05:25:40.628667+00:00`. They do not certify an unrun later revision.

- [Detailed recorded validation](reports/practical-workflows-2026-11-09.md)
- [Current Actions](https://github.com/JasonStys/business-knowledge-workbench/actions) records later integration checks separately.
- Preserve dated measurements and follow the existing testing guide to reproduce them; a test-source inventory alone does not establish execution.

## Practical boundaries

- Local owner-account edition; no shared hosted-business identity, invitations or managed tenant deployment is supplied.
- Numeric range search covers standardized cells, not OCR or arbitrary source-blob search; unit conversion uses canonical six-place precision.
- Export ZIPs are plaintext integrity records, not encrypted or digitally signed; they omit originals and account secrets.
- Import and conversion support is adapter-specific; no universal file-format, image/equation understanding or AI-provider compatibility is promised.

## Maintaining these editions

Update the editable usage/design/test documents first. Rebuild and visually review every Word page and workbook tab before replacing an edition; verify the exact binary digests and evidence source in publications.json. Keep account data, logs with secrets, installed-app state and private test stores out of documentation. Source and release assets retain their existing security and licensing boundaries.
