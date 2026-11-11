# Desktop maintenance and persistence validation — 10 November 2026

Author: Jason Stys. This edition records the 1.4.1 source candidate and its actual
locally built Windows application image. It supplements the historical validation
editions; it does not rewrite their source identities or imply that this candidate
has already replaced the installed 1.4.0 app.

## Corrections

The product catalog and document-preview labels contained damaged UTF-8 punctuation.
Those literal strings now render their intended separator, arrow and dash. The
installed 1.4.0 app failed the new exact-arrow negative control; this distinguishes
a real product correction from a screenshot-only change. The browser test first
navigates to Product catalog explicitly because owner accounts start in the
administration view.

The service now bundles official Python 3.14.10 and the desktop uses Electron
44.11.0. The older installed one-file service was independently identified as
Python 3.12.10 using its extracted DLL version metadata, without executing that
extracted DLL. The new frozen service refuses another interpreter before opening
private account storage or conversion-child dispatch. Native acceptance checks
the actual interpreter returned by health.

The native journey now quits, restarts, authenticates the same synthetic account,
unlocks the same vault and compares its retained document records. It retains the
existing encrypted account format, standard revisions, permitted library search,
custom layout/field options, unit normalization and selection-based ZIP exports.

## Observed local results

| Gate | Result |
| --- | --- |
| Complete source suite on Python 3.14.10 | 327 passed; 89.79% server coverage against the unchanged 80% floor |
| Frozen-runtime cases | Seven passed, including refusal before conversion dispatch and preservation of normal source mode |
| Private browser journeys | 18 passed across Chromium, Firefox and WebKit, including the visible-symbol regressions |
| Actual patched Windows executable | Passed: private login, custom standard preview, document imports/search/export, lock, same-account restart and retained encrypted library |
| Runtime observed through the actual service | Python 3.14.10; Electron shell 44.11.0 |
| Release safety | Numeric draft lookup, immutable version/tag policy, descriptor-bound output checks, twelve-asset completeness and exact-main prerequisite gates are covered by source tests |

The release workflow assembles a draft and performs a GET-only final verification.
It cannot publish. Draft visibility requires the documented repository permission,
while artifact upload remains serialized to avoid incomplete assets from a second
platform. Independent downloaded-package and installer acceptance precede final
publication. The current local pilot is not evidence that macOS/Linux packages,
hosted CI or an operating-system upgrade have passed; those remain delivery gates.

Source tests initially stalled in the restricted tool sandbox while asyncio
created its internal loopback socket pair. A diagnostic traceback and successful
repeat of all five adapter tests in normal context identified the environment
restriction. The full suite above then passed normally; no product code or test
expectation was weakened to work around the sandbox.

All application journeys used synthetic temporary accounts and documents.
Existing user accounts and data, Desktop icons and Docker were unchanged during
candidate validation. The actual installer update must preserve those separately.
Packages are unsigned. See the [release notes](../releases/v1.4.1.md) and
[official Python security release notice](https://www.python.org/downloads/release/python-31410/).
