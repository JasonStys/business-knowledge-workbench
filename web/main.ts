/* @index-begin
 * @symbol type: View L127
 * @symbol variable/parameter: state L136
 * @symbol variable/parameter: app L150
 * @symbol variable/parameter: navigationBusy L151
 * @symbol variable/parameter: disabledControls L152
 * @symbol variable/parameter: busy L158
 * @symbol function/class: navigationLock L158
 * @symbol variable/parameter: node L164
 * @symbol variable/parameter: cents L181
 * @symbol variable/parameter: money L181
 * @symbol function/class: esc L189
 * @symbol variable/parameter: value L189
 * @symbol variable/parameter: character L192
 * @symbol function/class: api L200
 * @symbol variable/parameter: init L200
 * @symbol variable/parameter: path L200
 * @symbol variable/parameter: headers L201
 * @symbol variable/parameter: [key, value] L212
 * @symbol variable/parameter: mutation L217
 * @symbol variable/parameter: separator L222
 * @symbol variable/parameter: response L223
 * @symbol variable/parameter: error L235
 * @symbol variable/parameter: message L248
 * @symbol function/class: notice L248
 * @symbol function/class: action L256
 * @symbol variable/parameter: work L256
 * @symbol function/class: shell L269
 * @symbol variable/parameter: workspace L270
 * @symbol variable/parameter: item L271
 * @symbol variable/parameter: [view, label, index] L280
 * @symbol variable/parameter: button L288
 * @symbol variable/parameter: event L301
 * @symbol variable/parameter: selected L303
 * @symbol function/class: loginView L339
 * @symbol variable/parameter: data L344
 * @symbol function/class: catalog L363
 * @symbol variable/parameter: content L364
 * @symbol variable/parameter: unit L370
 * @symbol variable/parameter: products L382
 * @symbol variable/parameter: update L385
 * @symbol variable/parameter: query L386
 * @symbol variable/parameter: filtered L389
 * @symbol variable/parameter: product L389
 * @symbol variable/parameter: spec L398
 * @symbol variable/parameter: result L409
 * @symbol function/class: chart L421
 * @symbol variable/parameter: report L421
 * @symbol variable/parameter: max L422
 * @symbol variable/parameter: point L422
 * @symbol function/class: dashboard L427
 * @symbol variable/parameter: employee L428
 * @symbol variable/parameter: format L431
 * @symbol variable/parameter: reportLink L432
 * @symbol variable/parameter: options L442
 * @symbol variable/parameter: customerOptions L443
 * @symbol variable/parameter: [id, label] L444
 * @symbol variable/parameter: form L458
 * @symbol variable/parameter: body L484
 * @symbol variable/parameter: title L519
 * @symbol variable/parameter: answer L537
 * @symbol function/class: documentList L552
 * @symbol variable/parameter: offset L552
 * @symbol variable/parameter: docs L556
 * @symbol variable/parameter: staff L558
 * @symbol variable/parameter: endpoint L559
 * @symbol variable/parameter: id L559
 * @symbol variable/parameter: suffix L559
 * @symbol variable/parameter: doc L562
 * @symbol variable/parameter: input L585
 * @symbol function/class: preview L594
 * @symbol variable/parameter: block L603
 * @symbol variable/parameter: index L603
 * @symbol variable/parameter: warning L603
 * @symbol variable/parameter: exports L608
 * @symbol variable/parameter: preferred L609
 * @symbol variable/parameter: available L610
 * @symbol variable/parameter: link L615
 * @symbol variable/parameter: url L618
 * @symbol variable/parameter: note L633
 * @symbol variable/parameter: standardLink L636
 * @symbol variable/parameter: copy L651
 * @symbol variable/parameter: close L682
 * @symbol function/class: download L695
 * @symbol variable/parameter: filename L695
 * @symbol variable/parameter: type L695
 * @symbol function/class: studio L705
 * @symbol variable/parameter: config L708
 * @symbol variable/parameter: history L709
 * @symbol variable/parameter: audit L713
 * @symbol variable/parameter: [dimension, units] L722
 * @symbol variable/parameter: [key, alias] L731
 * @symbol variable/parameter: readConfig L746
 * @symbol variable/parameter: key L754
 * @symbol variable/parameter: [, unit] L755
 * @symbol variable/parameter: section L759
 * @symbol variable/parameter: source L778
 * @symbol variable/parameter: draft L791
 * @symbol variable/parameter: frame L795
 * @symbol variable/parameter: entry L808
 * @symbol function/class: render L848
 * @symbol variable/parameter: previous L849
 * @symbol function/class: start L875
 * @symbol variable/parameter: privateMode L894
@index-end */
/** Accessible workspace UI and explicit API actions. Function/state lines: docs/code-index.md.
 * All user/source values are escaped. Canonical documents render inside scriptless sandbox frames.
 */
import "./style.css";
import {
  privateGate,
  isPrivate,
  decorateWorkbench,
  logout,
  modelHeaders,
} from "./private";
import type {
  Answer,
  Bootstrap,
  Config,
  DocumentResult,
  Product,
  Report,
  Session,
} from "./types";

type View = "catalog" | "customer" | "employee" | "admin";
import { standardFields, readStandard, measurementExample } from "./standards";
import { mountFieldEditor } from "./standard-builder";
import {
  libraryTools,
  libraryQuery,
  updateFacets,
  type LibraryResult,
} from "./library";
const state: {
  bootstrap?: Bootstrap;
  session: Session | null;
  workspace: string;
  view: View;
  selected: Set<string>;
  config?: Config;
  previewUrl?: string;
} = {
  session: null,
  workspace: "industrial",
  view: "catalog",
  selected: new Set(),
};
const app = document.querySelector<HTMLDivElement>("#app")!;
let navigationBusy = false;
const disabledControls = new WeakMap<
  HTMLButtonElement | HTMLSelectElement,
  boolean
>();

/** Keep asynchronous views/actions from overwriting a newer navigation; the private lock remains available. */
function navigationLock(busy: boolean): void {
  navigationBusy = busy;
  document
    .querySelectorAll<HTMLButtonElement | HTMLSelectElement>(
      "[data-view], #workspace, #private-tools, #sign-in, #content button",
    )
    .forEach((node) => {
      if (busy) {
        if (!disabledControls.has(node))
          disabledControls.set(node, node.disabled);
        node.disabled = true;
      } else if (disabledControls.has(node)) {
        node.disabled = disabledControls.get(node)!;
        disabledControls.delete(node);
      }
    });
}
// Async views insert controls before their final API read completes. Disable those
// newly inserted actions in the same microtask turn, rather than dropping a user's click.
new MutationObserver(() => {
  if (navigationBusy) navigationLock(true);
}).observe(app, { childList: true, subtree: true });
/** Format exact-cent values for cards; full exact cents remain available in reports. */
const money = (cents: number): string =>
  new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 2,
  }).format(cents / 100);

/** Escape untrusted values once at every template boundary. */
function esc(value: unknown): string {
  return String(value).replace(
    /[&<>"']/g,
    (character) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        character
      ]!,
  );
}

/** Same-origin JSON/multipart client; CSRF is sent only to this application's API. */
async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (isPrivate) {
    headers.set("X-KBW-Request", "v1");
    headers.set(
      "X-KBW-View",
      state.view === "catalog"
        ? "visitor"
        : state.view === "customer"
          ? "customer"
          : state.view,
    );
    for (const [key, value] of Object.entries(modelHeaders(path)))
      headers.set(key, value);
  }
  if (state.session && init.method && init.method !== "GET")
    headers.set("X-CSRF-Token", state.session.csrf);
  const mutation = Boolean(
    init.method && !["GET", "HEAD"].includes(init.method),
  );
  if ((init.body || mutation) && !(init.body instanceof FormData))
    headers.set("Content-Type", "application/json");
  const separator = path.includes("?") ? "&" : "?";
  const response = await fetch(
    isPrivate
      ? `/private/api/${path}${separator}workspace=${encodeURIComponent(state.workspace)}`
      : `/api/${path}`,
    {
      ...init,
      ...(mutation && !init.body ? { body: "{}" } : {}),
      headers,
      credentials: "same-origin",
    },
  );
  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => ({ detail: "Request failed" }));
    throw new Error(
      typeof error.detail === "string"
        ? error.detail
        : "Validation failed. Check field formats.",
    );
  }
  return response.json() as Promise<T>;
}

/** Present errors and completion status without replacing the active user form. */
function notice(message: string, error = false): void {
  const node = document.querySelector("#notice")!;
  if (!node) return;
  node.textContent = message;
  node.className = error ? "notice error" : "notice";
}

/** Route all async interaction failures to an accessible status region. */
async function action(work: () => Promise<void>): Promise<void> {
  if (navigationBusy) return;
  navigationLock(true);
  try {
    await work();
  } catch (error) {
    notice(error instanceof Error ? error.message : "Unexpected failure", true);
  } finally {
    navigationLock(false);
  }
}

/** Generate the stable, responsive navigation shell; tab selection never confers authorization. */
function shell(): void {
  const workspace = state.bootstrap?.workspaces.find(
    (item) => item.id === state.workspace,
  );
  app.innerHTML = `<aside class="sidebar"><a class="brand" href="/" aria-label="Workbench home"><span class="brand-mark">W</span><span>Workbench<small>BUSINESS KNOWLEDGE</small></span></a><div class="sidebar-label">YOUR WORKSPACE</div><label class="scenario-label" for="workspace">Business scenario</label><select id="workspace">${state.bootstrap?.workspaces.map((item) => `<option value="${esc(item.id)}" ${item.id === state.workspace ? "selected" : ""}>${esc(item.title)}</option>`).join("")}</select><nav aria-label="Workspace views">${[
    ["catalog", "Product catalog", "01"],
    ["customer", "Customer portal", "02"],
    ["employee", "Business workspace", "03"],
    ["admin", "Configuration studio", "04"],
  ]
    .map(
      ([view, label, index]) =>
        `<button data-view="${view}" ${state.view === view ? 'aria-current="page"' : ""}><span class="nav-number" aria-hidden="true">${index}</span>${label}</button>`,
    )
    .join(
      "",
    )}</nav><div class="sidebar-bottom"><span class="status-dot"></span> Modular by design<p>One structured source.<br>Many useful perspectives.</p><span class="version">${isPrivate ? "PRIVATE LOCAL EDITION · V1.3" : "LEGACY ROLE DEMO · V1.3"}</span></div></aside><div class="layout"><header><span class="breadcrumb">${esc(workspace?.title)} <span>/ ${esc(state.view === "admin" ? "Configuration studio" : state.view === "catalog" ? "Product catalog" : "Knowledge workspace")}</span></span><div class="account">${state.session ? `<span>${esc(state.session.username)} · ${esc(state.session.role)}</span><button id="logout" class="quiet">Sign out</button>` : '<span>Visitor access</span><button id="sign-in" class="quiet">Sign in</button>'}</div></header><main id="main" tabindex="-1"><div class="eyebrow">STRUCTURE YOUR INFORMATION. MAKE IT USEFUL.</div><div id="notice" class="notice" role="status" aria-live="polite"></div><div id="content"></div></main><footer>Business Knowledge Workbench <span>All scenario records are synthetic. No operational or financial advice.</span></footer></div>`;
  document
    .querySelectorAll<HTMLButtonElement>("[data-view]")
    .forEach((button) =>
      button.addEventListener(
        "click",
        () =>
          void action(async () => {
            state.view = button.dataset.view as View;
            state.selected.clear();
            await render();
          }),
      ),
    );
  document.querySelector("#workspace")!.addEventListener(
    "change",
    (event) =>
      void action(async () => {
        const selected = (event.target as HTMLSelectElement).value;
        if (!state.bootstrap?.workspaces.some((item) => item.id === selected))
          throw new Error("Unknown workspace selection.");
        if (state.session && !isPrivate)
          await api("logout", { method: "POST" });
        if (!isPrivate) state.session = null;
        state.workspace = selected;
        state.selected.clear();
        await render();
      }),
  );
  document
    .querySelector("#sign-in")
    ?.addEventListener("click", () => loginView());
  document.querySelector("#logout")?.addEventListener("click", () => {
    if (isPrivate) {
      void logout().catch((error) =>
        notice(
          error instanceof Error ? error.message : "Sign out failed",
          true,
        ),
      );
      return;
    }
    void action(async () => {
      await api("logout", { method: "POST" });
      state.session = null;
      state.view = "catalog";
      await render();
    });
  });
  decorateWorkbench();
  navigationLock(navigationBusy);
}

/** Present real credential authentication with an explicit development-only demo shortcut. */
function loginView(): void {
  document.querySelector("#content")!.innerHTML =
    `<section class="login panel"><div class="eyebrow">SCOPED ACCESS</div><h1>Enter your workspace</h1><p>Permissions are verified by the server. Customers see only their assigned records.</p>${state.bootstrap?.demo ? '<div class="demo-note">Demo mode uses synthetic records. Demo password: <code>workbench-demo</code></div>' : ""}<form id="login"><label for="username">Username</label><input id="username" name="username" autocomplete="username" value="${state.view === "admin" ? "admin" : state.view === "employee" ? "employee" : "customer"}" required><label for="password">Password</label><input id="password" name="password" type="password" autocomplete="current-password" required><button class="primary">Sign in securely</button></form></section>`;
  document.querySelector("#login")!.addEventListener("submit", (event) => {
    event.preventDefault();
    const data = new FormData(event.target as HTMLFormElement);
    void action(async () => {
      state.session = await api<Session>("login", {
        method: "POST",
        body: JSON.stringify({
          workspace: state.workspace,
          username: data.get("username"),
          password: data.get("password"),
        }),
      });
      state.view =
        state.session.role === "admin" ? "admin" : state.session.role;
      await render();
      notice("Signed in. Server-side permissions are active.");
    });
  });
}

/** Render product cards and normalized specifications from the real database. */
async function catalog(): Promise<void> {
  const content = document.querySelector("#content")!;
  content.innerHTML = `<div class="page-title"><div><h1>Find the right product.</h1><p>A clear catalog. Consistent specifications. Documentation that stays connected.</p></div><span class="pill">PUBLIC CATALOG</span></div><div class="hero-strip"><div><span class="hero-label">CONNECTED KNOWLEDGE</span><h2>From scattered files<br>to a shared understanding.</h2><p>${esc(state.bootstrap?.workspaces.find((item) => item.id === state.workspace)?.context)}</p></div><div class="hero-flow"><span>Source files</span><b>→</b><span>Canonical HTML</span><b>→</b><span>Search · Reports · AI</span></div></div><div class="section-heading"><h2>Explore products</h2><label class="search-label" for="search">Search catalog<input id="search" type="search" placeholder="Product name, ID, or capability"></label></div><div id="products" class="product-grid"></div><section class="panel units-panel"><div><h2>A common language for measurements</h2><p>Explicit units, exact decimal arithmetic and dimension checks.</p></div><form id="units"><label>Value<input name="value" type="text" inputmode="decimal" value="1" required></label><label>From<select name="source">${Object.values(
    state.bootstrap!.units,
  )
    .flat()
    .map(
      (unit) => `<option ${unit === "in" ? "selected" : ""}>${unit}</option>`,
    )
    .join("")}</select></label><label>To<select name="target">${Object.values(
    state.bootstrap!.units,
  )
    .flat()
    .map(
      (unit) => `<option ${unit === "mm" ? "selected" : ""}>${unit}</option>`,
    )
    .join(
      "",
    )}</select></label><button class="primary">Convert</button><output id="unit-result" aria-live="polite">1 in = 25.4 mm</output></form></section><div class="section-heading"><h2>Public documentation</h2></div><div id="documents"></div><div id="preview"></div>`;
  const products = await api<Product[]>(
    `products?workspace=${encodeURIComponent(state.workspace)}`,
  );
  const update = (): void => {
    const query = (
      document.querySelector("#search") as HTMLInputElement
    ).value.toLowerCase();
    const filtered = products.filter((product) =>
      `${product.id} ${product.name} ${product.description}`
        .toLowerCase()
        .includes(query),
    );
    document.querySelector("#products")!.innerHTML =
      filtered
        .map(
          (product) =>
            `<article class="product-card"><div class="product-code">${esc(product.id)} <span>↗</span></div><div class="product-illustration" aria-hidden="true"><div class="device"><span></span><span></span><span></span><span></span></div></div><span class="category">${esc(product.category)}</span><h3>${esc(product.name)}</h3><p>${esc(product.description)}</p><dl>${product.specifications.map((spec) => `<div><dt>${esc(spec.dimension)}</dt><dd>${esc(spec.value)} ${esc(spec.unit)}</dd></div>`).join("")}</dl><div class="card-bottom"><span>${money(product.price_cents)}</span><span>USD · ${isPrivate ? "recorded list price" : "synthetic list price"}</span></div></article>`,
        )
        .join("") ||
      '<p class="empty">No matching products. Try a product ID.</p>';
  };
  update();
  document.querySelector("#search")!.addEventListener("input", update);
  document.querySelector("#units")!.addEventListener("submit", (event) => {
    event.preventDefault();
    const data = new FormData(event.target as HTMLFormElement);
    void action(async () => {
      const result = await api<{ value: string; unit: string }>("units", {
        method: "POST",
        body: JSON.stringify(Object.fromEntries(data)),
      });
      document.querySelector("#unit-result")!.textContent =
        `${data.get("value")} ${data.get("source")} = ${result.value} ${result.unit}`;
    });
  });
  await documentList();
}

/** Accessible revenue chart with its complete numerical table below it. */
function chart(report: Report): string {
  const max = Math.max(...report.series.map((point) => point.revenue_cents), 1);
  return `<div class="chart" role="img" aria-label="Monthly revenue bar chart. Exact values are in the table below.">${report.series.map((point) => `<div><span class="bar" style="height:${Math.max(2, (point.revenue_cents / max) * 140)}px"></span><span>${point.month.slice(5)}</span></div>`).join("")}</div><details><summary>View accessible revenue data</summary><div class="table-scroll"><table><caption>Monthly product sales (USD)</caption><thead><tr><th>Month</th><th>Units</th><th>Revenue</th></tr></thead><tbody>${report.series.map((point) => `<tr><td>${point.month}</td><td>${point.quantity}</td><td>${money(point.revenue_cents)}</td></tr>`).join("")}</tbody></table></div></details>`;
}

/** Customer and employee dashboards use identical API contracts but different server scopes. */
async function dashboard(): Promise<void> {
  const employee = state.session?.role !== "customer";
  const data = await api<Report>("report");
  document.querySelector("#content")!.innerHTML =
    `<div class="page-title"><div><h1>${employee ? "Your knowledge, connected." : "Your products. Your perspective."}</h1><p>${employee ? "Organize evidence, normalize data, and turn information into something actionable." : "Sales, performance and documentation for your assigned customer account."}</p></div><span class="pill">${employee ? "STAFF WORKSPACE" : "CUSTOMER-SCOPED"}</span></div><div class="metrics"><div><span>Recorded revenue</span><strong>${money(data.revenue_cents)}</strong><small>USD · selected account scope</small></div><div><span>Units sold</span><strong>${data.quantity.toLocaleString()}</strong><small>${data.series.length} recorded months</small></div><div><span>Conversion standard</span><strong>HTML first</strong><small>Structured · traceable · portable</small></div></div><section class="panel"><div class="section-heading"><div><h2>Business performance</h2><p>Historical records, not live telemetry.</p></div><button id="report-download" class="quiet">Download report JSON</button></div>${chart(data)}${data.forecast.length ? `<div class="forecast"><h3>Three-month baseline projection</h3>${data.forecast.map((point) => `<div><span>Month +${point.month_offset}</span><strong>${money(point.revenue_cents)}</strong><small>${money(point.low_cents)} – ${money(point.high_cents)}</small></div>`).join("")}</div>` : ""}<p class="muted">${esc(data.method)}</p></section>${employee ? `<section class="panel"><h2>Bring information together</h2><p>Import supported documents or mapped sales data. Original sources and conversion evidence are retained.</p><form id="import" class="import-form"><label>Source file<input type="file" name="file" required accept="${state.bootstrap!.formats.map((format) => "." + format).join(",")}"></label><label>Visibility<select name="visibility"><option value="internal">Internal only</option><option value="customer">Customer account</option><option value="public">Public</option></select></label><label>Customer<select name="customer"><option value="north">North account</option><option value="south">South account</option></select></label><label>Category<input name="category" value="Imported" maxlength="40" required></label><label class="check"><input name="dataset" type="checkbox" value="true">Import sales rows into reporting</label><button class="primary">Import & standardize</button></form><p class="muted">4 MiB maximum. ${state.bootstrap!.formats.join(", ")}. Unsupported or uncertain content is not silently interpreted.</p></section>` : ""}<section class="panel"><div class="section-heading"><h2>Document library</h2><span>ACL enforced before search</span></div>${libraryTools()}${employee ? '<div class="merge-tools"><label>Compilation title<input id="merge-title" value="Business evidence pack" maxlength="120"></label><button id="merge" class="quiet">Combine selected documents</button></div>' : ""}<div id="documents"></div><div id="preview"></div></section><section class="panel"><div class="section-heading"><div><h2>Ask your knowledge workspace</h2><p>Optional, read-only AI with authorized source citations. Disabled until an admin enables it.</p></div><span class="pill">HUMAN REVIEW REQUIRED</span></div><form id="ask"><label for="question">Question</label><div class="ask-row"><input id="question" required minlength="3" maxlength="800" placeholder="What do the controller specifications say about width?"><button class="primary">Ask sources</button></div></form><div id="answer" class="answer" aria-live="polite"></div></section>`;
  const reportLink = document.createElement("a");
  reportLink.className = "quiet";
  reportLink.download = "";
  reportLink.href = `${isPrivate ? "/private" : ""}/api/report/export/${encodeURIComponent(data.standard.default_export)}?workspace=${encodeURIComponent(state.workspace)}`;
  reportLink.textContent = `Download standard report ${data.standard.default_export.toUpperCase()}`;
  document.querySelector("#report-download")!.after(reportLink);
  if (data.standard.enforce_export)
    document.querySelector<HTMLButtonElement>("#report-download")!.hidden =
      true;
  if (employee) {
    const options = await api<{ customers: Record<string, string> }>("options");
    const customerOptions = Object.entries(options.customers)
      .map(([id, label]) => `<option value="${esc(id)}">${esc(label)}</option>`)
      .join("");
    document.querySelector<HTMLSelectElement>(
      '#import select[name="customer"]',
    )!.innerHTML = customerOptions;
    document
      .querySelector("#import")!
      .closest("section")!
      .insertAdjacentHTML(
        "beforebegin",
        `<section class="panel"><details><summary>Add a product / assigned inventory record</summary><p>New public catalog entries are assigned to one customer group in this reference schema. Keep private service data in customer-scoped documents.</p><form id="product" class="import-form"><label>Product ID<input name="id" pattern="[A-Z0-9-]{2,32}" required placeholder="MC-320"></label><label>Product name<input name="name" minlength="2" maxlength="100" required></label><label>Product category<input name="category" minlength="2" maxlength="60" required></label><label>Description<input name="description" minlength="2" maxlength="1000" required></label><label>Price (USD cents)<input name="price_cents" type="number" min="0" max="1000000000" step="1" required></label><label>Assigned account<select name="customer">${customerOptions}</select></label><label>Specifications<input name="specifications" maxlength="5000" placeholder="Width 2 in; mass 400 g"></label><button class="primary">Create product</button></form></details></section>`,
      );
    document.querySelector("#product")!.addEventListener("submit", (event) => {
      event.preventDefault();
      const form = new FormData(event.target as HTMLFormElement);
      void action(async () => {
        await api("products", {
          method: "POST",
          body: JSON.stringify({
            ...Object.fromEntries(form),
            price_cents: Number(form.get("price_cents")),
          }),
        });
        await dashboard();
        notice("Product added with an HTML-first public specification.");
      });
    });
  }
  document
    .querySelector("#report-download")!
    .addEventListener("click", () =>
      download(
        JSON.stringify(data, null, 2),
        "business-report.json",
        "application/json",
      ),
    );
  document.querySelector("#import")?.addEventListener("submit", (event) => {
    event.preventDefault();
    const form = event.target as HTMLFormElement;
    const body = new FormData(form);
    const button = form.querySelector("button")!;
    button.disabled = true;
    notice("Converting in a bounded worker. Please wait…");
    void action(async () => {
      try {
        const result = await api<{ id: string; duplicate: boolean }>("import", {
          method: "POST",
          body,
        });
        await dashboard();
        notice(
          result.duplicate
            ? "Source already imported; no duplicate records created."
            : "Source converted to HTML and stored with provenance.",
        );
        await preview(result.id);
      } finally {
        button.disabled = false;
      }
    });
  });
  document
    .querySelector("#library-search")!
    .addEventListener("submit", (event) => {
      event.preventDefault();
      void action(() => documentList());
    });
  document.querySelector("#library-search")!.addEventListener("reset", () => {
    window.setTimeout(() => void action(() => documentList()), 0);
  });
  document.querySelector("#merge")?.addEventListener(
    "click",
    () =>
      void action(async () => {
        const title = (
          document.querySelector("#merge-title") as HTMLInputElement
        ).value;
        const result = await api<{ id: string }>("merge", {
          method: "POST",
          body: JSON.stringify({ ids: [...state.selected], title }),
        });
        state.selected.clear();
        await documentList();
        await preview(result.id);
        notice(
          "Compilation created as internal-only, preserving source references.",
        );
      }),
  );
  document.querySelector("#ask")!.addEventListener("submit", (event) => {
    event.preventDefault();
    void action(async () => {
      const answer = await api<Answer>("ask", {
        method: "POST",
        body: JSON.stringify({
          question: (document.querySelector("#question") as HTMLInputElement)
            .value,
        }),
      });
      document.querySelector("#answer")!.innerHTML =
        `<p>${esc(answer.answer)}</p><small>${esc(answer.provider)} · ${esc(answer.notice)}</small><p>Source IDs: ${answer.citations.map(esc).join(", ") || "None"}</p>`;
    });
  });
  await documentList();
}

/** Search standardized content with scoped facets, stable pages and direct downloads. */
async function documentList(offset = 0): Promise<void> {
  const result = await api<LibraryResult>(
    `library?${libraryQuery(state.workspace, offset)}`,
  );
  const docs = result.items;
  updateFacets(result.facets);
  const staff = state.session && state.session.role !== "customer";
  const endpoint = (id: string, suffix: string): string =>
    `${isPrivate ? "/private" : ""}/api/documents/${encodeURIComponent(id)}/${suffix}?workspace=${encodeURIComponent(state.workspace)}`;
  document.querySelector("#documents")!.innerHTML =
    `<p role="status">Showing ${result.total ? result.offset + 1 : 0}–${Math.min(result.offset + docs.length, result.total)} of ${result.total} permitted files</p><div class="table-scroll"><table><caption>${docs.length} accessible documents</caption><thead><tr>${staff ? "<th>Select</th>" : ""}<th>Document and content</th><th>Category / format</th><th>Access</th><th>Extraction</th><th>Open / download</th></tr></thead><tbody>${docs.map((doc) => `<tr>${staff ? `<td><input type="checkbox" data-select="${esc(doc.id)}" aria-label="Select ${esc(doc.title)}" ${state.selected.has(doc.id) ? "checked" : ""}></td>` : ""}<td>${esc(doc.title)}<details><summary>Content excerpt</summary><p>${esc(doc.excerpt)}</p></details><small>Standard revision ${esc(doc.standard_revision ?? "legacy")} · ${esc(doc.created)}</small></td><td>${esc(doc.category)} · ${esc(doc.source_format || "internal")}</td><td><span class="tag">${esc(doc.visibility)}</span></td><td>${esc(doc.review_status)}</td><td><button class="link-button" data-doc="${esc(doc.id)}" aria-label="Preview ${esc(doc.title)}">Preview ↗</button><a download href="${endpoint(doc.id, "export/" + encodeURIComponent(doc.standard_format))}" aria-label="Download standardized ${esc(doc.title)}">Download ${esc(doc.standard_format.toUpperCase())}</a></td></tr>`).join("") || '<tr><td colspan="6">No accessible documents match these filters.</td></tr>'}</tbody></table></div><div class="button-row"><button type="button" id="library-prev" class="quiet" ${offset === 0 ? "disabled" : ""}>Previous files</button><button type="button" id="library-next" class="quiet" ${offset + docs.length >= result.total ? "disabled" : ""}>Next files</button></div>`;
  document
    .querySelector("#library-prev")!
    .addEventListener(
      "click",
      () => void action(() => documentList(Math.max(0, offset - result.limit))),
    );
  document
    .querySelector("#library-next")!
    .addEventListener(
      "click",
      () => void action(() => documentList(offset + result.limit)),
    );
  document
    .querySelectorAll<HTMLButtonElement>("[data-doc]")
    .forEach((button) =>
      button.addEventListener(
        "click",
        () => void action(() => preview(button.dataset.doc!)),
      ),
    );
  document
    .querySelectorAll<HTMLInputElement>("[data-select]")
    .forEach((input) =>
      input.addEventListener("change", () => {
        if (input.checked) state.selected.add(input.dataset.select!);
        else state.selected.delete(input.dataset.select!);
      }),
    );
}

/** Preview canonical HTML in a sandbox, expose uncertainty, and offer HTML-first exports. */
async function preview(id: string): Promise<void> {
  const result = await api<DocumentResult>(
    `documents/${encodeURIComponent(id)}?workspace=${encodeURIComponent(state.workspace)}`,
  );
  if (state.previewUrl) URL.revokeObjectURL(state.previewUrl);
  state.previewUrl = URL.createObjectURL(
    new Blob([result.html], { type: "text/html" }),
  );
  document.querySelector("#preview")!.innerHTML =
    `<section class="document-preview"><div class="section-heading"><h3>${esc(result.title)}</h3><span class="pill">${esc(result.review_status)}</span></div>${result.warnings.length ? `<div class="warning"><strong>Review extraction fidelity</strong><ul>${result.warnings.map((warning) => `<li>${esc(warning)}</li>`).join("")}</ul></div>` : ""}<iframe title="Canonical document preview" sandbox=""></iframe><div class="exports"></div><details><summary>Machine-readable provenance and unit conversions</summary><pre>${esc(JSON.stringify({ provenance: result.provenance, measurements: result.measurements }, null, 2))}</pre></details>${state.session?.role !== "customer" && state.session ? result.blocks.map((block, index) => (block.kind === "figure" ? `<button class="quiet" data-vision="${index}">Request unverified vision analysis: figure ${index + 1}</button>` : "")).join("") : ""}<div id="vision-answer" class="answer"></div></section>`;
  // URL values stay in DOM properties, never reinterpreted as HTML attribute syntax.
  document.querySelector<HTMLIFrameElement>("#preview iframe")!.src = isPrivate
    ? `/private/api/documents/${encodeURIComponent(id)}/preview?workspace=${encodeURIComponent(state.workspace)}`
    : state.previewUrl;
  const exports = document.querySelector("#preview .exports")!;
  const preferred = result.standard?.output_standard.default_export;
  const available =
    result.standard?.output_standard.enforce_export && preferred
      ? [preferred]
      : state.bootstrap!.exports;
  for (const format of [...available, "source"]) {
    const link = document.createElement("a");
    const suffix =
      format === "source" ? "source" : `export/${encodeURIComponent(format)}`;
    const url = new URL(
      `${isPrivate ? "/private" : ""}/api/documents/${encodeURIComponent(id)}/${suffix}`,
      location.origin,
    );
    url.searchParams.set("workspace", state.workspace);
    link.href = url.href;
    link.className = "quiet";
    link.download = "";
    link.textContent =
      format === "source"
        ? "Original source"
        : `Export ${format.toUpperCase()}`;
    exports.append(link);
  }
  if (preferred) {
    const note = document.createElement("p");
    note.textContent = `${result.standard!.name} · Revision ${result.standard!.revision} · Standard file type: ${preferred.toUpperCase()}`;
    exports.prepend(note);
    const standardLink = document.createElement("a");
    standardLink.href = `${isPrivate ? "/private" : ""}/api/documents/${encodeURIComponent(id)}/export/${encodeURIComponent(preferred)}?workspace=${encodeURIComponent(state.workspace)}`;
    standardLink.className = "primary";
    standardLink.download = "";
    standardLink.textContent = `Download standard ${preferred.toUpperCase()}`;
    exports.prepend(standardLink);
  }
  if (state.session && state.session.role !== "customer") {
    const button = document.createElement("button");
    button.className = "quiet";
    button.textContent = "Create current-standard copy";
    button.addEventListener(
      "click",
      () =>
        void action(async () => {
          const copy = await api<{ id: string; duplicate: boolean }>(
            `documents/${encodeURIComponent(id)}/standardize`,
            { method: "POST" },
          );
          await documentList();
          await preview(copy.id);
          notice(
            copy.duplicate
              ? "A matching current-standard document already exists; original unchanged."
              : "Current-standard copy created; original evidence and sales unchanged.",
          );
        }),
    );
    exports.append(button);
  }
  document
    .querySelectorAll<HTMLButtonElement>("[data-vision]")
    .forEach((button) =>
      button.addEventListener(
        "click",
        () =>
          void action(async () => {
            const answer = await api<Answer>(
              `documents/${encodeURIComponent(id)}/vision/${button.dataset.vision}`,
              { method: "POST" },
            );
            document.querySelector("#vision-answer")!.textContent =
              answer.answer + " " + answer.notice;
          }),
      ),
    );
  const close = document.createElement("button");
  close.type = "button";
  close.className = "quiet";
  close.textContent = "Close document preview";
  close.addEventListener("click", () => {
    if (state.previewUrl) URL.revokeObjectURL(state.previewUrl);
    delete state.previewUrl;
    document.querySelector("#preview")!.replaceChildren();
  });
  exports.append(close);
}

/** Download a browser-generated report; revoke its temporary blob URL after activation. */
function download(value: string, filename: string, type: string): void {
  const url = URL.createObjectURL(new Blob([value], { type }));
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

/** Admin configuration studio edits validated data and displays the actual server adapter/revision. */
async function studio(): Promise<void> {
  const result = await api<{ config: Config; ai_adapter: string }>("config");
  state.config = result.config;
  const config = result.config;
  const history =
    await api<
      { revision: number; actor: string; created: string; config: Config }[]
    >("standards/history");
  const audit =
    await api<
      { actor: string; event: string; detail: string; created: string }[]
    >("audit");
  document.querySelector("#content")!.innerHTML =
    `<div class="page-title"><div><h1>Adapt the workbench.</h1><p>Change the business profile without changing the application skeleton.</p></div><span class="pill">ADMIN / DEVELOPER</span></div><div class="config-layout"><section class="panel"><h2>Active configuration</h2><p>Revision ${config.revision} · Profile ${esc(config.profile)} · Adapter ${esc(result.ai_adapter)}</p><form id="config"><label>Workspace title<input name="title" value="${esc(config.title)}" minlength="2" maxlength="60" required></label><div class="config-units">${Object.entries(
      state.bootstrap!.units,
    )
      .map(
        ([dimension, units]) =>
          `<label>${esc(dimension)} target<select name="unit-${dimension}"><option value="">Keep source units</option>${units.map((unit) => `<option ${config.units[dimension] === unit ? "selected" : ""}>${unit}</option>`).join("")}</select></label>`,
      )
      .join(
        "",
      )}</div><label>Document section order<input name="sections" value="${esc(config.sections.join(", "))}" required></label><p class="muted">Available sections: overview, content, measurements, provenance. Include content exactly once.</p><label class="check"><input name="forecasting" type="checkbox" ${config.forecasting ? "checked" : ""}>Enable baseline forecasting</label><label class="check"><input name="ai_enabled" type="checkbox" ${config.ai_enabled ? "checked" : ""}>Enable read-only AI (external providers may receive authorized document content)</label><h3>Sales column mapping</h3><div class="config-units">${Object.entries(
      config.data_columns,
    )
      .map(
        ([key, alias]) =>
          `<label>${key}<input name="column-${key}" value="${esc(alias)}" maxlength="40" required></label>`,
      )
      .join(
        "",
      )}</div><button class="primary">Save validated configuration</button></form></section><section class="panel"><h2>Configuration in use</h2><pre>${esc(JSON.stringify(config, null, 2))}</pre><h3>Extension boundaries</h3><p>Importers → semantic blocks → canonical HTML → exports.</p><p>AI adapters receive scoped JSON evidence, never database access. Own model settings and source consent are in Account, AI &amp; help for private mode; trusted deployment settings apply only to the separate legacy engine.</p><p>Existing conversions keep their original revision. Reimport a source to apply changed normalization or templates.</p></section></div><section class="panel"><h2>Operational audit trail</h2><div class="table-scroll"><table><caption>Latest 50 configuration and import events</caption><thead><tr><th>Time</th><th>Actor</th><th>Event</th><th>Reference</th></tr></thead><tbody>${audit.map((item) => `<tr><td>${esc(item.created)}</td><td>${esc(item.actor)}</td><td>${esc(item.event)}</td><td>${esc(item.detail)}</td></tr>`).join("") || '<tr><td colspan="4">No recorded changes yet.</td></tr>'}</tbody></table></div></section>`;
  document
    .querySelector("#config button")!
    .insertAdjacentHTML(
      "beforebegin",
      standardFields(config) +
        `<label>Customer accounts (JSON ID-to-label map)<textarea name="customers" rows="5" required>${esc(JSON.stringify(config.customers, null, 2))}</textarea></label>`,
    );
  const form = document.querySelector<HTMLFormElement>("#config")!;
  mountFieldEditor();
  const readConfig = (): Config => {
    const data = new FormData(form);
    return {
      ...config,
      title: String(data.get("title")),
      customers: JSON.parse(String(data.get("customers"))),
      units: Object.fromEntries(
        Object.keys(state.bootstrap!.units)
          .map((key) => [key, String(data.get("unit-" + key))])
          .filter(([, unit]) => unit),
      ),
      sections: String(data.get("sections"))
        .split(",")
        .map((section) => section.trim()),
      output_standard: readStandard(data, config),
      data_columns: Object.fromEntries(
        Object.keys(config.data_columns).map((key) => [
          key,
          String(data.get("column-" + key)),
        ]),
      ),
      forecasting: data.has("forecasting"),
      ai_enabled: data.has("ai_enabled"),
    };
  };
  document
    .querySelector("#standard-example")!
    .addEventListener("click", measurementExample);
  document.querySelector("#standard-preview")!.addEventListener(
    "click",
    () =>
      void action(async () => {
        const source = document.querySelector<HTMLInputElement>(
          "#standard-preview-file",
        )!.files?.[0];
        let body: FormData | string;
        if (source) {
          body = new FormData();
          body.set("file", source);
          body.set("config", JSON.stringify(readConfig()));
        } else
          body = JSON.stringify({
            config: readConfig(),
            sample: new FormData(form).get("std-sample"),
          });
        const draft = await api<DocumentResult>(
          source ? "standards/preview-file" : "standards/preview",
          { method: "POST", body },
        );
        const frame = document.querySelector<HTMLIFrameElement>(
          "#standard-preview-frame",
        )!;
        frame.srcdoc = draft.html;
        frame.hidden = false;
        document.querySelector("#standard-preview-status")!.textContent =
          "Draft preview only — not saved. " + draft.warnings.join(" ");
      }),
  );
  document
    .querySelector(".config-layout")!
    .insertAdjacentHTML(
      "afterend",
      `<section class="panel"><h2>Standard revision history</h2><p>Restore creates a new revision, never rewrites a historical document. At most 250 saved revisions per business profile.</p><label>Revision to restore<select id="standard-history">${history.map((entry) => `<option value="${entry.revision}">${entry.revision} — ${esc(entry.config.output_standard.name)} — ${esc(entry.created)}</option>`).join("")}</select></label><button id="standard-restore" class="quiet">Restore as new revision</button></section>`,
    );
  document.querySelector("#standard-restore")!.addEventListener(
    "click",
    () =>
      void action(async () => {
        await api("standards/restore", {
          method: "POST",
          body: JSON.stringify({
            revision: Number(
              document.querySelector<HTMLSelectElement>("#standard-history")!
                .value,
            ),
            expected_revision: config.revision,
          }),
        });
        state.bootstrap = await api<Bootstrap>("bootstrap");
        await render();
        notice(
          "Historical standard restored as a new revision. Existing documents were not changed.",
        );
      }),
  );
  document.querySelector("#config")!.addEventListener("submit", (event) => {
    event.preventDefault();
    void action(async () => {
      await api("config", {
        method: "PUT",
        body: JSON.stringify(readConfig()),
      });
      state.bootstrap = await api<Bootstrap>("bootstrap");
      await render();
      notice(
        "Configuration saved. Revision increased; original conversions were preserved.",
      );
    });
  });
}

/** Resolve view requirements and keep forbidden roles from misleadingly accessing admin UI. */
async function render(): Promise<void> {
  const previous = navigationBusy;
  navigationLock(true);
  try {
    if (state.previewUrl) {
      URL.revokeObjectURL(state.previewUrl);
      delete state.previewUrl;
    }
    shell();
    if (state.view === "catalog") return await catalog();
    if (!state.session) return loginView();
    if (
      (state.view === "admin" && state.session.role !== "admin") ||
      (state.view === "employee" && state.session.role === "customer")
    ) {
      document.querySelector("#content")!.innerHTML =
        '<section class="panel"><h1>This view requires a different role.</h1><p>Sign out and sign in with an authorized staff or administrator account.</p></section>';
      return;
    }
    if (state.view === "admin") return await studio();
    return await dashboard();
  } finally {
    navigationLock(previous);
  }
}

/** Bootstrap the app and install a shell-only service worker that never caches API responses. */
async function start(): Promise<void> {
  state.bootstrap = await api<Bootstrap>("bootstrap");
  state.session = await api<Session | null>("session");
  if (isPrivate)
    state.session = {
      username: "Local owner",
      role: "admin",
      workspace: state.workspace,
      csrf: "internal-only",
    };
  if (state.session) {
    state.workspace = state.session.workspace;
    state.view = state.session.role;
  }
  await render();
  if (!isPrivate && "serviceWorker" in navigator && import.meta.env.PROD)
    await navigator.serviceWorker.register("/sw.js");
}
void privateGate(start)
  .then((privateMode) => {
    if (!privateMode) return start();
  })
  .catch((error) => {
    app.innerHTML = `<main><h1>Workbench is unavailable</h1><p>${esc(error instanceof Error ? error.message : "Start the API service and reload.")}</p></main>`;
  });
