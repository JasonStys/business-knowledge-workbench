# Private local application release checklist

Author: Jason Stys. Public backend deployment is not authorized; release means source and local desktop downloads.

Before release: verify clean scoped diff, no tracked accounts/keys/databases, sanitized source history/fixtures, locked deps and licenses, Python coverage >=80%, lint/format/typecheck, exact source/file maps, actual rich conversions/exports, browser accessibility/privacy/lock/reopen and three-OS frozen+packaged journeys. Inspect Actions artifact bytes and available billing meter; no cleanup without new approval.

The manual release gate uses an exact source commit with successful Validate workbench and Desktop packages runs. Draft v1.1.0 is tied to that source; only tested platform binaries and SHA-256 records are uploaded to Releases. Publish waits for all OS jobs. Never upload private roots or raw real-user test traces.

After release: independently download/verify Windows portable bytes and launch the extracted application in a disposable test root. Then launch its normal empty private root and show the local website without creating an actual user credential. Recheck latest validation/CodeQL/native/release conclusions, install notices and final storage usage. Preserve other installed apps and legacy data.

Rollback trigger: any source isolation leak, corrupt round-trip, unexpected external traffic, lost recovery state, failed actual packaged conversion or failing required CI. Keep release draft until repaired. After publication, issue a new version for behavioral fixes rather than retagging tested binaries. Preserve old accounts and backups; never erase recovery data during rollback. Installers are unsigned/not notarized; verification is provenance checking, not a security guarantee.
