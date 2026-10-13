# Architecture decision for private local workspaces

Status: accepted. Version: 1.1. Author: Jason Stys.

The existing business engine supports scoped document extraction, normalization, sales and configuration, but its demo accounts and plaintext developer database are unsuitable as the default installed product. The chosen design preserves the engine behind a new loopback account boundary. Browser/native clients have no filesystem selectors, imports of executable model factories or global provider-key fallback.

## Alternatives and decision

A hosted multi-tenant service would need hosting, HTTPS, operations, account recovery/delivery, staff membership design and a different privacy model; public hosting is out of scope by user choice. Browser-only encrypted data cannot run the existing Python parsers on the same document bytes. Sharing one unlocked database across logged-in accounts would break privacy.

Each local account instead owns an exclusive engine database and model settings, protected by an independent encryption phrase. One engine is unlocked at a time. A new session needs its own key proof. Own catalog/customer/employee previews lower visibility within that owner's profiles; they do not create actual shared-user roles. An account cookie alone cannot read another account or an already-unlocked workspace without proof.

The outer ASGI boundary validates literal Host/port, Origin, fetch-site, custom request header, cookie ownership and body budget before routes. Private proxy serializes requests against lock/snapshot/config lifecycle and injects trusted owner/profile/preview identity, never a caller-selected owner/database path. It preserves existing engine ACLs, source provenance and HTML-first export functions. Public legacy API routes are absent on the private app.

Scrypt hashes protect login passwords; independent browser PBKDF2-derived AES keys protect locked archives. Streaming ZIP_STORED plus AES-GCM authenticates all bytes before extraction. SQLite online backup prevents an inconsistent archive; atomic replacement preserves old ciphertext on disk failure. Portable-name/link/duplicate/file-count/size checks precede restore.

## Costs and boundaries

The service and OS are trusted while processing plaintext. Crash recovery can leave plaintext until the owner seals again. No claim of protection against an administrator, malware or a modified app. One account engine is bounded rather than a scalable concurrent collaboration platform.

Document parsing remains a credential-stripped, 25-second subprocess, with input/archive/page/row/pixel/output limits. It does not execute uploaded scripts/macros, but third-party parsers can have unknown vulnerabilities; container/CDR isolation for adversarial uploads is future deployment work. Docker on the user's computer is not modified.

Metadata-only unchanged snapshots are O(F); changed encryption is O(S) in stored bytes with bounded chunks. DB write stop is 128 MiB, recovery reserve 160 MiB, archive 512 MiB/2,000 files. Original 4 MiB input and 200-document-per-profile limits remain. Reports/query results have bounded materialization; constant fragment allowlists and bound SQL parameters prevent interpolated sort/injection.

Electron uses a sandboxed, isolated ephemeral renderer, no Node or privileged preload, no permissions/popups, and only owned loopback/blob requests. The native process alone holds shutdown authorization. Exact nonce-ready verification avoids connecting to an unrelated port listener. Published installers contain source/build runtime, UI and dependency notices, never account data.

New runtime roots do not migrate, alter or remove legacy data. Downgrade by closing the new app and using a separately backed-up prior version; do not point old versions at new account directories. Native signing/notarization, mobile stores, shared tenants and public hosting are not shipped.
