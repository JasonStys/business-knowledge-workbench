# Installed Windows application validation 10 November 2026

By Jason Stys. This edition documents actual published **1.4.1** installed
bytes built from `ba3cf3cfc6f2d443747f7350af06ca0329b1fcc4`. Earlier Office editions retain their
historical source baselines and byte identities.

## Observed results

Full installed import/preview/custom-standard/library/export journey and same-account vault restart passed with synthetic rich documents.

Real 1.4.0 and 1.4.1 apps reopened the same account; all 10 document metadata records and full semantic documents matched exactly.

327 tests at 89.79 percent coverage,18 private browser journeys, current main/CodeQL and all 3 OSnative release builds passed. All 12 downloaded assets matched provider/sidecar hashes.

Verified opaque account/launcher backup, installer exit 0 and unchanged normal profile bytes. Existing Desktop and extra demo links were preserved; the main link targets the accepted updated EXE.

## Illustrated workflow and implementation

The [four-page application guide](windows-application-guide-1.4.1.docx) contains actual installed
application screenshots, prepared inputs used within the full app, operating
steps and important code excerpts from the immutable runtime source. Every page
was inspected and the OOXML schema passed validation. The [review manifest](windows-application-guide-1.4.1.json)
records Word, screenshot, source and rendered-page identities.

## User data and limits

Use the matching 1.4.1 Windows installer and checksum sidecar from Releases. It upgrades the per-user app without requiring a system Python installation. Other OS packages are separate downloads.

Private account archives are outside the install/repository in BusinessKnowledgeWorkbenchAccounts. Back up the complete directory and preserve the independent vault phrase; login recovery cannot decrypt a lost vault phrase.

Supported formats are parsed with explicit fidelity warnings; there is no claim to understand every file, image, handwritten equation or arbitrary embedded object. External AI/provider use requires separate configuration and consent.

The native private edition isolates each authenticated owner's vault. Role previews are not an enterprise staff-directory authorization system. Packages are unsigned; the trusted OS/service can access active plaintext while the owner unlocks it. Docker and normal account credentials were not accessed by acceptance.

Desktop and Start-menu target identities were verified where created. A complete
actual installed executable journey is separate from normal shortcut activation;
this report does not claim an additional manual shortcut-button test. No Docker
configuration, real credential or existing account data was used by the synthetic
acceptance. Prepared scenarios are inputs to the full product, never separate demo
applications.

This documentation commit must pass its own hosted checks. Earlier runtime results
do not certify future source changes.
