# Private local application release checklist

Author: Jason Stys. Public backend deployment is not authorized; release means source and local desktop downloads.

Before release: verify clean scoped diff, no tracked accounts/keys/databases, sanitized source history/fixtures, locked deps and licenses, Python coverage >=80%, lint/format/typecheck, exact source/file maps, actual rich conversions/exports, browser accessibility/privacy/lock/reopen and three-OS frozen+packaged journeys. Inspect Actions artifact bytes and available billing meter; no cleanup without new approval.

The manual release gate uses an exact source commit with successful Validate workbench, CodeQL and Desktop packages runs. Draft v1.4.0 is tied to that source; only tested platform binaries and SHA-256 records are uploaded to Releases. Publish waits for all OS jobs. Never upload private roots or raw real-user test traces. The native journey exercises draft/publish/schema import/current-standard copy/restore, visual field controls, actual file previews, correlated searches and downloads in addition to real rich-document conversion and encrypted locking.

Python validation, browser, packaging and release jobs install locked dependencies
in a dedicated `.venv`; runner-global tools are not part of the app environment.
Keep `pip check` enabled. A failed unpublished candidate may be retargeted only
after its jobs stop, with all exact-source gates rerun and every platform rebuilt
and tested. Never retarget a published version.

After release: independently download/verify Windows portable bytes and launch the extracted application in a disposable test root. Then launch its normal empty private root and show the local website without creating an actual user credential. Recheck latest validation/CodeQL/native/release conclusions, install notices and final storage usage. Preserve other installed apps and legacy data.

Rollback trigger: any source isolation leak, corrupt round-trip, unexpected external traffic, lost recovery state, failed actual packaged conversion or failing required CI. Keep release draft until repaired. After publication, issue a new version for behavioral fixes rather than retagging tested binaries. Preserve old accounts and backups; never erase recovery data during rollback. Installers are unsigned/not notarized; verification is provenance checking, not a security guarantee.
