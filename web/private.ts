/* @index-begin
 * @symbol type: Account L59
 * @symbol type: Provider L68
 * @symbol variable/parameter: isPrivate L74
 * @symbol variable/parameter: current L75
 * @symbol variable/parameter: revision L76
 * @symbol variable/parameter: consent L77
 * @symbol variable/parameter: lastActivity L78
 * @symbol variable/parameter: idleSeconds L79
 * @symbol variable/parameter: poll L80
 * @symbol variable/parameter: root L81
 * @symbol function/class: escape L84
 * @symbol variable/parameter: value L84
 * @symbol variable/parameter: c L87
 * @symbol function/class: privateApi L95
 * @symbol variable/parameter: path L96
 * @symbol variable/parameter: data L97
 * @symbol variable/parameter: method L98
 * @symbol variable/parameter: response L100
 * @symbol variable/parameter: body L109
 * @symbol variable/parameter: bytes L120
 * @symbol function/class: encoded L120
 * @symbol function/class: derive L125
 * @symbol variable/parameter: phrase L125
 * @symbol variable/parameter: salt L125
 * @symbol variable/parameter: material L128
 * @symbol function/class: task L152
 * @symbol variable/parameter: work L152
 * @symbol variable/parameter: error L155
 * @symbol variable/parameter: node L156
 * @symbol function/class: heading L164
 * @symbol function/class: auth L169
 * @symbol variable/parameter: mode L169
 * @symbol variable/parameter: button L174
 * @symbol variable/parameter: event L177
 * @symbol variable/parameter: form L179
 * @symbol variable/parameter: result L182
 * @symbol variable/parameter: panel L185
 * @symbol function/class: help L198
 * @symbol function/class: gate L203
 * @symbol variable/parameter: key L231
 * @symbol variable/parameter: onReady L239
 * @symbol function/class: privateGate L241
 * @symbol variable/parameter: callback L242
 * @symbol variable/parameter: next L256
 * @symbol variable/parameter: notice L273
 * @symbol function/class: activity L295
 * @symbol function/class: ready L303
 * @symbol variable/parameter: settings L304
 * @symbol function/class: logout L312
 * @symbol function/class: decorateWorkbench L318
 * @symbol variable/parameter: footer L320
 * @symbol function/class: tools L333
 * @symbol function/class: modelHeaders L399
@index-end */
/** Jason Stys: real local account UI, independent encryption phrase, help and explicit AI consent.
 * Keys/credentials stay in memory only; never use local/session storage or URL tokens.
 */
type Account = {
  alias: string;
  configured: boolean;
  salt: string | null;
  unlocked: boolean;
  engine_busy: boolean;
  save_failed: boolean;
  recovery_pending: boolean;
};
type Provider = {
  endpoint: string;
  model: string;
  revision: string;
  has_key: boolean;
};
export let isPrivate = false;
let current: Account | null = null;
let revision = "";
let consent = false;
let lastActivity = 0;
let idleSeconds = 600;
let poll: ReturnType<typeof setInterval> | undefined;
const root = (): HTMLElement => document.querySelector("#app")!;

/** Escape display values from account aliases and API state. */
function escape(value: string): string {
  return value.replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        c
      ]!,
  );
}

/** Same-origin private account calls with CSRF-resistant custom headers and no persistence. */
export async function privateApi<T>(
  path: string,
  data?: unknown,
  method = "POST",
): Promise<T> {
  const response = await fetch("/private/" + path, {
    method: data === undefined ? "GET" : method,
    credentials: "same-origin",
    headers:
      data === undefined
        ? {}
        : { "Content-Type": "application/json", "X-KBW-Request": "v1" },
    ...(data === undefined ? {} : { body: JSON.stringify(data) }),
  });
  const body = await response
    .json()
    .catch(() => ({ detail: "Local request failed" }));
  if (!response.ok)
    throw Object.assign(new Error(body.detail || "Local request failed"), {
      status: response.status,
    });
  return body as T;
}

/** Encode bounded random bytes without retaining secrets in browser storage. */
function encoded(bytes: Uint8Array): string {
  return btoa(String.fromCharCode(...bytes));
}

/** Derive an independent AES key using browser WebCrypto; never send the human phrase. */
async function derive(phrase: string, salt: string): Promise<string> {
  if (phrase.length < 15 || phrase.length > 256)
    throw new Error("Vault phrase must be 15–256 characters.");
  const material = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(phrase),
    "PBKDF2",
    false,
    ["deriveBits"],
  );
  return encoded(
    new Uint8Array(
      await crypto.subtle.deriveBits(
        {
          name: "PBKDF2",
          salt: Uint8Array.from(atob(salt), (c) => c.charCodeAt(0)),
          iterations: 600000,
          hash: "SHA-256",
        },
        material,
        256,
      ),
    ),
  );
}

/** Render a bounded form error without reflecting credentials or server internals. */
async function task(work: () => Promise<void>): Promise<void> {
  try {
    await work();
  } catch (error) {
    const node = document.querySelector("#account-status");
    if (node)
      node.textContent =
        error instanceof Error ? error.message : "Operation failed safely";
  }
}

/** Public attribution and local-data boundary are visible before registration. */
function heading(): string {
  return '<div class="private-heading"><span class="brand-mark">W</span><p>BUSINESS KNOWLEDGE WORKBENCH · LOCAL EDITION</p><h1>Your information. Your workspace.</h1><p>Organize documents, products and sales without a hosted account or background data collection.</p><p>Created by <strong>Jason Stys</strong> · <a href="https://github.com/JasonStys" target="_blank" rel="noreferrer">GitHub</a> · <a href="https://www.linkedin.com/in/jason-stys-31b30b351/" target="_blank" rel="noreferrer">Contact / LinkedIn</a></p></div>';
}

/** Create/login/recover local accounts; recovery resets login only, never decrypts a vault. */
function auth(mode = "register"): void {
  root().classList.add("private-entry");
  root().innerHTML = `<main id="main" tabindex="-1" class="private-home">${heading()}<section class="panel account-panel"><h2>${mode === "register" ? "Create your local account" : mode === "reset" ? "Recover your login" : "Sign in to your account"}</h2><p>Use an alias, not an email address. No account information is sent to Jason.</p><form id="account-form"><label>Account alias<input name="alias" pattern="[a-z0-9_][a-z0-9_-]{2,39}" minlength="3" maxlength="40" autocomplete="username" required></label><label>Login password<input name="password" type="password" minlength="15" maxlength="128" autocomplete="${mode === "login" ? "current-password" : "new-password"}" required></label>${mode === "reset" ? '<label>Recovery code<input name="recovery" type="password" required minlength="32" maxlength="128"></label>' : ""}<button class="primary">${mode === "register" ? "Create account" : mode === "reset" ? "Reset login" : "Sign in"}</button></form><div id="account-status" role="status"></div><div class="account-options"><button data-auth="login">Sign in instead</button><button data-auth="register">Create another account</button><button data-auth="reset">Recover login</button></div><details><summary>Privacy and setup help</summary>${help()}</details></section></main>`;
  document
    .querySelectorAll<HTMLButtonElement>("[data-auth]")
    .forEach((button) => (button.onclick = () => auth(button.dataset.auth!)));
  document
    .querySelector("#account-form")!
    .addEventListener("submit", (event) => {
      event.preventDefault();
      const form = event.target as HTMLFormElement;
      const data = Object.fromEntries(new FormData(form));
      void task(async () => {
        const result = await privateApi<{ recovery?: string }>(mode, data);
        form.reset();
        if (result.recovery) {
          const panel = document.querySelector(".account-panel")!;
          panel.innerHTML = `<h2>Save your recovery code</h2><p>Shown once. Store it privately. It recovers login, not your vault phrase.</p><pre id="recovery-code">${escape(result.recovery)}</pre><button id="continue" class="primary">I saved my recovery code</button><div id="account-status" role="status"></div>`;
          document.querySelector<HTMLButtonElement>("#continue")!.onclick =
            () => {
              if (mode === "reset") auth("login");
              else void task(gate);
            };
        } else await gate();
      });
    });
}

/** Explain actual capabilities, irreversible encryption and trusted-device boundaries. */
function help(): string {
  return "<p>1. Create an alias and long login password; privately save your recovery code. 2. Set a different vault phrase and remember it: there is no recovery/backdoor for this phrase. 3. Open Business workspace to add products, import files, search, combine and export. 4. Configuration studio changes units, document sections, column mappings and optional AI.</p><p>Each account owns three initially empty business profiles. Sample data is imported only when you explicitly choose Load synthetic examples. Customer and employee views are previews of your own profile—not shared-user permissions. This release does not invite coworkers or host public catalogs.</p><p>Imports are limited to supported formats, 4 MiB per file and 200 documents per profile. HTML is sanitized; previews have no scripts. PDFs, figures and equations may need human review; there is no universal OCR or image understanding.</p><p>Save and lock before switching accounts or quitting. Records and own API settings are AES-256-GCM encrypted when locked, but temporarily plaintext on this trusted device while processing. Your OS administrator, malware or a compromised app can inspect active data. No app can guarantee protection against a compromised computer.</p><p>Download encrypted snapshot after saving. To restore on another device, close the app and copy the entire private account data directory (including accounts.sqlite and encrypted folder). The snapshot alone does not include login/key configuration. Forgotten vault phrases cannot be reset. Plaintext exports and any old developer/demo data need separate protection.</p><p>No analytics, ads, hosted accounts or automatic external AI calls. Optional AI sends selected authorized sources only after destination-specific consent. API providers have their own privacy/retention rules. Model answers are unverified and never modify records. Native desktop releases are unsigned; verify checksums and download only from Jason Stys’s repository.</p>";
}

/** Restore a session without decrypting anything until this browser proves its own vault phrase. */
async function gate(): Promise<void> {
  try {
    current = await privateApi<Account>("account");
  } catch {
    current = null;
    auth();
    return;
  }
  if (current.unlocked) {
    await ready();
    return;
  }
  root().classList.add("private-entry");
  root().innerHTML = `<main id="main" tabindex="-1" class="private-home">${heading()}<section class="panel account-panel"><h2>Unlock your private business workspace</h2><p>Signed in as ${escape(current.alias)}. ${current.configured ? "Enter your independent vault phrase." : "Choose an independent vault phrase. Losing it means losing access to encrypted documents."}</p>${current.engine_busy ? '<p class="warning">Another account has the local engine unlocked. It must lock first.</p>' : ""}${current.recovery_pending ? '<p class="warning">Interrupted workspace detected. Only its owner can recover it.</p>' : ""}<form id="unlock-form"><label>Vault phrase<input name="phrase" type="password" minlength="15" maxlength="256" required autocomplete="off"></label>${!current.configured ? '<label>Confirm vault phrase<input name="confirmation" type="password" minlength="15" maxlength="256" required autocomplete="off"></label>' : ""}<button class="primary">Unlock workspace</button></form><div id="account-status" role="status"></div><button id="account-logout">Sign out</button><details><summary>Help and privacy</summary>${help()}</details></section></main>`;
  document.querySelector<HTMLButtonElement>("#account-logout")!.onclick = () =>
    void task(logout);
  document
    .querySelector("#unlock-form")!
    .addEventListener("submit", (event) => {
      event.preventDefault();
      const form = event.target as HTMLFormElement;
      const data = new FormData(form);
      void task(async () => {
        const phrase = String(data.get("phrase"));
        if (!current!.configured && phrase !== data.get("confirmation"))
          throw new Error("Vault phrases do not match.");
        const salt =
          current!.salt || encoded(crypto.getRandomValues(new Uint8Array(16)));
        const key = await derive(phrase, salt);
        form.reset();
        await privateApi("unlock", { key, salt });
        await gate();
      });
    });
}

let onReady: () => Promise<void>;
/** Verify private mode before revealing any document shell; legacy mode is separate explicit demo use. */
export async function privateGate(
  callback: () => Promise<void>,
): Promise<boolean> {
  const response = await fetch("/health", { cache: "no-store" });
  if (response.status === 404) return false;
  const data = await response.json();
  if (!response.ok || data.mode !== "private-local-accounts")
    throw new Error("Unknown service mode; private access disabled");
  isPrivate = true;
  onReady = callback;
  await gate();
  if (!poll)
    poll = setInterval(() => {
      if (current?.unlocked)
        void task(async () => {
          let next: Account;
          try {
            next = await privateApi<Account>("account");
          } catch (error) {
            if ((error as { status?: number }).status === 401) {
              current = null;
              consent = false;
              auth("login");
              return;
            }
            throw error;
          }
          if (!next.unlocked) {
            current = next;
            await gate();
          }
          if (next.save_failed) {
            const notice = document.querySelector("#notice");
            if (notice)
              notice.textContent =
                "Encrypted save failed. Preserve recovery data and free disk space before locking.";
          }
        });
    }, 5000);
  document.addEventListener("pointerdown", activity);
  document.addEventListener("keydown", activity);
  window.addEventListener("pagehide", () => {
    if (current?.unlocked)
      void fetch("/private/lock", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-KBW-Request": "v1" },
        body: "{}",
        keepalive: true,
      });
  });
  return true;
}

/** Intentional activity renews idle policy at most every thirty seconds; passive polling never does. */
function activity(): void {
  if (current?.unlocked && Date.now() - lastActivity > 30000) {
    lastActivity = Date.now();
    void privateApi("activity", { idle_seconds: idleSeconds }).catch(() => {});
  }
}

/** Load model destination state but never accept hidden/global provider keys. */
async function ready(): Promise<void> {
  const settings = await privateApi<Provider>("providers");
  revision = settings.revision;
  consent = false;
  root().classList.remove("private-entry");
  await onReady();
}

/** Seal before sign-out and clear all in-memory UI content by reloading the same local origin. */
export async function logout(): Promise<void> {
  await privateApi("logout", {});
  location.reload();
}

/** Attach private controls after each existing workspace-shell render. */
export function decorateWorkbench(): void {
  if (!isPrivate) return;
  const footer = document.querySelector("footer")!;
  footer.innerHTML =
    '<span>Created by Jason Stys · <a href="https://github.com/JasonStys" target="_blank" rel="noreferrer">GitHub</a> · <a href="https://www.linkedin.com/in/jason-stys-31b30b351/" target="_blank" rel="noreferrer">Contact</a></span><button id="private-tools" class="quiet">Account, AI & help</button><button id="private-lock" class="quiet">Lock workspace</button>';
  document.querySelector<HTMLButtonElement>("#private-lock")!.onclick = () =>
    void task(async () => {
      await privateApi("lock", {});
      location.reload();
    });
  document.querySelector<HTMLButtonElement>("#private-tools")!.onclick = () =>
    void task(tools);
}

/** Own local account management, snapshot, synthetic examples and destination-specific model configuration. */
async function tools(): Promise<void> {
  const settings = await privateApi<Provider>("providers");
  if (settings.revision !== revision) consent = false;
  revision = settings.revision;
  document.querySelector("#content")!.innerHTML =
    `<section class="panel"><h1>Account, AI & help</h1><p>Local account ${escape(current!.alias)} · one unlocked account per device engine.</p><div id="account-status" role="status"></div><button id="save-snapshot" class="primary">Save encrypted snapshot</button> <a class="quiet" href="/private/backup" download>Download encrypted snapshot</a><label>Lock after inactivity<select id="idle"><option value="600">10 minutes</option><option value="1800">30 minutes</option><option value="7200">2 hours</option></select></label><h2>Learn with fictional examples</h2><p>Explicitly adds synthetic products, documents and sales to your own empty profiles. Never loads old demo accounts or other people’s data.</p><button id="seed">Load synthetic examples</button><h2>Optional model connection</h2><p>Offline extractive reference is the default. Connect an OpenAI-compatible model on literal 127.0.0.1 or the official HTTPS chat endpoint. No arbitrary remote URLs, scripts or model downloads. Your key is never returned or placed in source.</p><form id="provider-form"><label>Endpoint (blank for offline)<input name="endpoint" value="${escape(settings.endpoint)}" maxlength="2048" placeholder="http://127.0.0.1:11434/v1/chat/completions"></label><label>Model<input name="model" value="${escape(settings.model)}" maxlength="128" required></label><label>Own API key<input name="key" type="password" maxlength="4096" autocomplete="off" placeholder="${settings.has_key ? "Credential saved privately" : "Optional for local models"}"></label><label class="check"><input name="retain_key" type="checkbox">Keep saved key (same destination only)</label><button class="primary">Save model settings</button></form><label class="check"><input id="source-consent" type="checkbox" ${consent ? "checked" : ""}>I approve sending authorized document excerpts / selected figures to ${escape(settings.endpoint || "the offline local reference")} for this session.</label><p>Enable AI separately in Configuration studio. Changing the destination invalidates consent. Hosted providers may collect the data you deliberately send.</p><h2>Usage, privacy & recovery</h2>${help()}<details><summary>Delete my local account</summary><p>Irreversible deletion of this account and live encrypted archive only. External backups and exported files remain.</p><form id="delete-form"><label>Current login password<input name="password" type="password" minlength="15" maxlength="128" required></label><label class="check"><input name="confirm" type="checkbox" required>I confirm permanent deletion</label><button>Delete my account</button></form></details></section>`;
  document.querySelector<HTMLSelectElement>("#idle")!.value =
    String(idleSeconds);
  document.querySelector<HTMLSelectElement>("#idle")!.onchange = (event) => {
    idleSeconds = Number((event.target as HTMLSelectElement).value);
    void task(async () => {
      await privateApi("activity", { idle_seconds: idleSeconds });
    });
  };
  document.querySelector<HTMLButtonElement>("#save-snapshot")!.onclick = () =>
    void task(async () => {
      await privateApi("save", {});
      document.querySelector("#account-status")!.textContent =
        "Encrypted snapshot saved. Cold backups require the full private account directory.";
    });
  document.querySelector<HTMLButtonElement>("#seed")!.onclick = () =>
    void task(async () => {
      await privateApi("seed", {});
      document.querySelector("#account-status")!.textContent =
        "Synthetic examples added only to empty profiles. Choose a workspace view to explore.";
    });
  document.querySelector<HTMLInputElement>("#source-consent")!.onchange = (
    event,
  ) => {
    consent = (event.target as HTMLInputElement).checked;
  };
  document
    .querySelector("#provider-form")!
    .addEventListener("submit", (event) => {
      event.preventDefault();
      const form = event.target as HTMLFormElement;
      const data = new FormData(form);
      void task(async () => {
        await privateApi(
          "providers",
          { ...Object.fromEntries(data), retain_key: data.has("retain_key") },
          "PUT",
        );
        form.reset();
        consent = false;
        await tools();
        document.querySelector("#account-status")!.textContent =
          "Model settings saved privately. Review destination and consent again.";
      });
    });
  document
    .querySelector("#delete-form")!
    .addEventListener("submit", (event) => {
      event.preventDefault();
      const data = new FormData(event.target as HTMLFormElement);
      void task(async () => {
        await privateApi("delete", {
          password: data.get("password"),
          confirm: data.has("confirm"),
        });
        location.reload();
      });
    });
}

/** Only per-session consent for the reviewed model revision unlocks external source transmission. */
export function modelHeaders(path: string): Record<string, string> {
  if (!isPrivate) return {};
  if (path === "ask" || path.includes("/vision/")) {
    if (!consent)
      throw new Error(
        "Review Account, AI & help and approve the selected destination first.",
      );
    return { "X-KBW-Provider-Revision": revision };
  }
  return {};
}
