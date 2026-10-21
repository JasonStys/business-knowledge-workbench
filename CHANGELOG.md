# Changelog

## 1.2.0 — 2026-10-21

- Added owner/admin-controlled output standards: named templates, section labels,
  print layout, table schemas/aliases/order, measurement dimensions and preferred
  or restricted delivery formats.
- Added non-persistent draft preview, atomic revision history, stale-write protection
  and restoration as a new revision; existing data/configuration are preserved.
- Added current-standard copies and report downloads; compilations now normalize
  preserved extracted values into one current unit contract instead of mixing revisions.
- Fixed same-bytes/different-format import deduplication and empty-body JSON
  requests without weakening CSRF, session or scriptless-preview boundaries.
- Added rich-format schema, injection, precision, authority, concurrency, encrypted
  history/isolation and actual browser/native workflow regressions.
- Patched audited Vite, Pillow, pypdf and certifi dependencies; updated the tested
  Playwright runtime. No arbitrary auto-upgrade or audit-gate suppression.
- Expanded the README around the primary standardization purpose and documented
  original-requirement coverage and limits rather than promising universal file/AI semantics.

Earlier private-account and navigation releases remain documented in
[v1.1.0](docs/releases/v1.1.0.md) and [v1.1.1](docs/releases/v1.1.1.md).
