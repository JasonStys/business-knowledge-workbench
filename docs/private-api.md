# Private local API

Author: Jason Stys. Use the exact loopback port printed by the CLI or launched by the installed app. No public hosting, CORS wildcard, URL bearer or operator-read API.

All mutating requests need `X-KBW-Request: v1`, matching Origin if sent, and JSON (multipart only for `/private/api/import`). Bounds are checked before private handlers: 4 MiB + 64,000 bytes. Account cookies are HttpOnly, SameSite Strict, port-named and restricted to `/private`. Responses are no-store and no-referrer. Source scripts/external resources are removed; authenticated preview HTML alone can be framed by this same origin and remains scriptless sandboxed.

| Route | Contract |
| --- | --- |
| GET /health | Public ready/version/creator/launch nonce, no records. |
| POST /private/register | Alias and 15–128 character password; once-shown recovery code. |
| POST /private/login | Existing alias/password, not vault unlock. |
| POST /private/reset | Alias, one-use recovery code and new password; seals before rotating/revoking. |
| GET /private/account | Own alias/key-configuration status only; no other owner's details. |
| POST /private/unlock | Base64 32-byte derived key; first-use 16-byte base64 salt; session-specific proof. |
| POST /private/activity | Unlocked human activity; idle_seconds 600, 1800 or 7200. |
| POST /private/save, /private/lock, /private/logout | Own checked snapshot/seal/revoke only. |
| POST /private/delete | Current password and confirm=true; deletes only that live account/archive. |
| GET /private/backup | Own encrypted archive only, no key/account metadata. |
| POST /private/seed | Explicit fictional samples to empty own profiles; no demo credentials. |
| GET/PUT /private/providers | Own endpoint/model/key availability; keys write-only. Destination changes cannot retain old keys. |
| /private/api/* | Preserved business API only after account+session vault proof. |
| POST /launcher/shutdown | Optional process-only launcher secret, never available to renderer. |

Business API route names are detailed in [api.md](api.md) for the preserved engine; in private mode prepend `/private` and pass a selected own profile (`workspace=industrial|renewable|laboratory`). The owner may preview `X-KBW-View=admin|employee|customer|visitor`; a preview is not an invitation or a grant to another person. Unknown profiles/views are rejected. Customer header selects a subset of this owner's records only. Legacy engine login/logout routes are blocked.

External AI requests additionally need `X-KBW-Provider-Revision` matching the destination configuration the user reviewed. With no configured endpoint, reference matching is entirely offline. Endpoint selection is limited to official HTTPS chat or literal loopback HTTP compatible servers on nonprivileged ports with exact chat-completions path; no arbitrary remote DNS/IP URL proxy. Responses and citations are validated and labeled unverified.

Errors: 401 login expired/required, 403 boundary/preview forbidden, 423 vault proof required, 409 state/config/consent/quota conflict, 415 unsupported file, 422 bounded validation/conversion rejection, 429 throttled, 502 model failed safely. Validation responses never echo submitted credentials. No caller-selected owner ID, root path, executable or arbitrary module field is accepted.
