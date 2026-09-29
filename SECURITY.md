# Security policy

This reference is intended for local synthetic-data evaluation. Do not deploy demo accounts with real records. Report vulnerabilities privately through GitHub's private vulnerability reporting when enabled; do not include secrets/customer sources in public issues.

Defense boundaries: server roles/workspace/customer ACLs; opaque expiring hashed sessions; scrypt password storage; CSRF and same-origin writes; sanitized HTML and scriptless previews; attachment-only raw sources; upload/archive/text/table/page/image limits and timed subprocesses; transactional mapped data and hash-based sales idempotency; no private PWA caching; model opt-in with scoped context and checked citations.

Non-guarantees: no complete parser sandbox, antivirus/CDR, universal OCR/vision, certified compliance, prompt-injection proof, SSO, account lifecycle, data retention/deletion, distributed rate limits or encrypted database at rest. Windows subprocess memory is not hard-limited by this code. Public uploads need dedicated hardened parser workers and resource/egress policy. A custom AI factory is trusted application code, not a safe way to run uploaded models/agents. Production secrets and model data transfers require operator review.

Dependency scans and CodeQL are evidence checks, not proof of absence of vulnerabilities. See [operations](docs/operations.md), [support limits](docs/formats.md) and [validation](docs/validation.md) for release details.
