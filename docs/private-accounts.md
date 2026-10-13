# Private local accounts and user guide

Business Knowledge Workbench 1.1 is a local app by Jason Stys. Accounts are on this device, not on GitHub or a hosted service. Every owner gets three initially empty business profiles and its own document database/model settings. One owner can unlock the local engine at a time. Customer/employee/catalog/admin tabs preview that owner's own data; this release has no shared-user invitations or remote public catalog.

## First use

Launch the downloaded application; use the menu to open its exact local website if preferred. Create a non-identifying alias and a 15–128 character login password. Save the once-shown random recovery code offline. Set a different 15–256 character vault phrase and confirm it. Browser WebCrypto derives a 256-bit key using PBKDF2-SHA256 (600,000 iterations and random 16-byte salt); the phrase is not transmitted or stored. The trusted local service receives that key only while unlocked.

Open Business workspace to add products or import documents. Supported source limits and fidelity warnings are in [formats.md](formats.md). Configuration studio changes unit targets, document section order, customer labels, sales columns and AI enablement. Historical conversions retain their original revision. Use Account, AI & help to explicitly load fictional examples, save/download snapshots, choose idle locking and configure an optional own model.

Customer preview uses the North subset; catalog preview sees public-labeled documents only. The owner can intentionally choose any preview—these are not security grants for employees. All externally unauthenticated document/source/export routes are blocked.

## Data and recovery

Windows data: `%LOCALAPPDATA%/BusinessKnowledgeWorkbenchAccounts`. macOS: `~/Library/Application Support/BusinessKnowledgeWorkbenchAccounts`. Linux: `$XDG_DATA_HOME/BusinessKnowledgeWorkbenchAccounts` (or `~/.local/share`). Installation files and Git contain no accounts or runtime records. The dedicated root is restricted to the OS user (plus SYSTEM/administrators on Windows).

Login passwords use salted scrypt N=2^17, r=8, p=1. Sessions and one-use login recovery codes are random secrets stored only as digests. Sessions expire after 8 hours or 30 minutes of request inactivity. Human-idle locking is separately 10 minutes by default, optionally 30 minutes/2 hours; background polling does not renew it. Each new session must prove its vault key even if another same-account session unlocked the engine.

Lock/sign out seals an authenticated AES-256-GCM archive and removes only this account's checked temporary working directory. Disk failures preserve the working files, key and prior archive; do not manually erase recovery state. A crash may leave recoverable plaintext; only its account can reopen it. Normal app shutdown requests graceful sealing.

Download snapshot after Save encrypted snapshot. For restoration, quit the app and make an OS-level backup of the entire protected directory including `accounts.sqlite`, all companion database files and `encrypted/`. Restore only into a compatible dedicated application directory. The downloaded archive alone lacks account/key configuration. Keep backups private. Login recovery rotates the password/code and revokes old sessions, **not the vault phrase**. Lost vault phrases cannot be recovered. Current-password confirmation deletes only the selected account and live archive; exports/backups remain.

## Optional AI and threats

Default extraction/reference matching is offline and is not an LLM or universal vision model. An own OpenAI-compatible local server on literal 127.0.0.1 or the official HTTPS chat endpoint can be selected. Keys stay in the account's encrypted settings; they are never returned. Review destination-specific consent each session and after any settings change, then enable AI in Configuration studio. Authorized excerpts/selected figures may leave the computer only for these deliberately requested model calls. There are no model tools, record writes, telemetry or background uploads.

Do not import malicious files on a sensitive workstation. Parsers are bounded/timed child processes without provider credentials, but not full OS exploit sandboxes or antivirus/CDR. The OS owner, administrator, malware or compromised extensions/app can inspect active plaintext and memory. This is not zero-knowledge against the local service. JSON/HTML/report exports can contain plaintext private evidence.

Help/contact: [Jason Stys GitHub](https://github.com/JasonStys), [LinkedIn](https://www.linkedin.com/in/jason-stys-31b30b351/). Jason has no automatic access to local accounts or documents.
