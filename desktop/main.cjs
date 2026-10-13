/* @index-begin
 * @symbol variable/parameter: { app, BrowserWindow, dialog, Menu, session, shell, } L45
 * @symbol variable/parameter: { spawn } L53
 * @symbol variable/parameter: { randomBytes } L54
 * @symbol variable/parameter: { join } L55
 * @symbol variable/parameter: net L56
 * @symbol variable/parameter: fs L57
 * @symbol variable/parameter: service L58
 * @symbol variable/parameter: serviceOrigin L58
 * @symbol variable/parameter: serviceToken L58
 * @symbol variable/parameter: closing L59
 * @symbol function/class: port L62
 * @symbol variable/parameter: server L63
 * @symbol variable/parameter: reject L64
 * @symbol variable/parameter: resolve L64
 * @symbol variable/parameter: selected L67
 * @symbol function/class: launch L73
 * @symbol variable/parameter: nonce L76
 * @symbol variable/parameter: resources L77
 * @symbol variable/parameter: executable L80
 * @symbol variable/parameter: ui L87
 * @symbol variable/parameter: log L91
 * @symbol variable/parameter: env L96
 * @symbol variable/parameter: exited L114
 * @symbol variable/parameter: code L118
 * @symbol variable/parameter: signal L118
 * @symbol variable/parameter: origin L124
 * @symbol variable/parameter: ready L126
 * @symbol variable/parameter: attempt L127
 * @symbol variable/parameter: response L129
 * @symbol variable/parameter: health L132
 * @symbol variable/parameter: isolated L146
 * @symbol variable/parameter: _permission L152
 * @symbol variable/parameter: _webContents L152
 * @symbol variable/parameter: callback L152
 * @symbol variable/parameter: details L156
 * @symbol variable/parameter: allowed L157
 * @symbol variable/parameter: window L165
 * @symbol variable/parameter: event L181
 * @symbol variable/parameter: url L181
 * @symbol variable/parameter: stopped L245
 * @symbol variable/parameter: error L286
@index-end */
/** Jason Stys: native private-account launcher. No renderer secrets, privileged preload or host code execution. */
const {
  app,
  BrowserWindow,
  dialog,
  Menu,
  session,
  shell,
} = require("electron");
const { spawn } = require("node:child_process");
const { randomBytes } = require("node:crypto");
const { join } = require("node:path");
const net = require("node:net");
const fs = require("node:fs");
let service, serviceOrigin, serviceToken;
let closing = false;

/** Reserve a local port; the owned Python service verifies binding and a random launch nonce. */
async function port() {
  const server = net.createServer();
  await new Promise((resolve, reject) =>
    server.once("error", reject).listen(0, "127.0.0.1", resolve),
  );
  const selected = server.address().port;
  await new Promise((resolve) => server.close(resolve));
  return selected;
}

/** Launch a private backend and an ephemeral sandboxed renderer, never forwarding global provider credentials. */
async function launch() {
  const selected = await port();
  serviceToken = randomBytes(32).toString("hex");
  const nonce = randomBytes(32).toString("hex");
  const resources = app.isPackaged
    ? process.resourcesPath
    : join(__dirname, "..", "release");
  const executable = join(
    resources,
    "service",
    process.platform === "win32"
      ? "business-knowledge-workbench-service.exe"
      : "business-knowledge-workbench-service",
  );
  const ui = app.isPackaged
    ? join(resources, "ui")
    : join(__dirname, "..", "dist");
  fs.mkdirSync(app.getPath("userData"), { recursive: true });
  const log = fs.openSync(
    join(app.getPath("userData"), "service.log"),
    "a",
    0o600,
  );
  const env = {
    ...process.env,
    KBW_LAUNCH_TOKEN: serviceToken,
    KBW_LAUNCH_NONCE: nonce,
    KBW_PARENT_PID: String(process.pid),
  };
  delete env.KB_DB;
  delete env.KB_AI_KEY;
  delete env.KB_AI_ENDPOINT;
  delete env.KB_AI_FACTORY;
  delete env.KB_LEGACY_MODE;
  delete env.KB_DEMO;
  service = spawn(
    executable,
    ["--port", String(selected), "--ui", ui, "--no-browser"],
    { env, windowsHide: true, stdio: ["ignore", log, log] },
  );
  fs.closeSync(log);
  let exited = false;
  service.once("error", () => {
    exited = true;
  });
  service.once("exit", (code, signal) => {
    if (process.env.KBW_DESKTOP_TEST)
      console.error("Private service exited", code, signal);
    exited = true;
    if (!closing) app.quit();
  });
  const origin = `http://127.0.0.1:${selected}`;
  serviceOrigin = origin;
  let ready = false;
  for (let attempt = 0; attempt < 180 && !exited; attempt++) {
    try {
      const response = await fetch(origin + "/health", {
        signal: AbortSignal.timeout(1000),
      });
      const health = response.ok ? await response.json() : {};
      ready =
        health.mode === "private-local-accounts" &&
        health.launcher_nonce === nonce;
    } catch {
      /* Unpacking/startup is bounded; no connection to an unrelated listener is accepted. */
    }
    if (ready) break;
    await new Promise((resolve) => setTimeout(resolve, 250));
  }
  if (!ready)
    throw new Error(
      "The private local service could not start. Preserve account recovery data; no uploaded document was executed.",
    );
  const isolated = session.fromPartition(
    "business-knowledge-workbench-ephemeral-" + nonce,
    {
      cache: false,
    },
  );
  isolated.setPermissionRequestHandler((_webContents, _permission, callback) =>
    callback(false),
  );
  isolated.setPermissionCheckHandler(() => false);
  isolated.webRequest.onBeforeRequest((details, callback) => {
    let allowed = false;
    try {
      allowed =
        new URL(details.url).origin === origin ||
        details.url.startsWith("blob:" + origin + "/");
    } catch {}
    callback({ cancel: !allowed });
  });
  const window = new BrowserWindow({
    width: 1440,
    height: 1000,
    minWidth: 420,
    minHeight: 600,
    show: false,
    backgroundColor: "#122338",
    webPreferences: {
      session: isolated,
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: true,
      webSecurity: true,
    },
  });
  window.webContents.setWindowOpenHandler(() => ({ action: "deny" }));
  window.webContents.on("will-navigate", (event, url) => {
    try {
      if (new URL(url).origin !== origin) event.preventDefault();
    } catch {
      event.preventDefault();
    }
  });
  window.once("ready-to-show", () => window.show());
  Menu.setApplicationMenu(
    Menu.buildFromTemplate([
      {
        label: "Workbench",
        submenu: [
          {
            label: "Open local website",
            click: () => {
              void shell.openExternal(origin + "/");
            },
          },
          { label: "Reload", role: "reload" },
          { label: "Quit", role: "quit" },
        ],
      },
      {
        label: "Edit",
        submenu: [
          { role: "undo" },
          { role: "redo" },
          { type: "separator" },
          { role: "cut" },
          { role: "copy" },
          { role: "paste" },
          { role: "selectAll" },
        ],
      },
      {
        label: "Help",
        submenu: [
          {
            label: "Jason Stys · GitHub",
            click: () => {
              void shell.openExternal("https://github.com/JasonStys");
            },
          },
          {
            label: "Contact Jason Stys · LinkedIn",
            click: () => {
              void shell.openExternal(
                "https://www.linkedin.com/in/jason-stys-31b30b351/",
              );
            },
          },
        ],
      },
    ]),
  );
  await window.loadURL(origin + "/");
}

/** Ask only the owned backend to cancel jobs and seal. Never force-delete recovery files on timeout. */
app.on("before-quit", (event) => {
  if (closing || !service || service.exitCode !== null) return;
  event.preventDefault();
  closing = true;
  const stopped = new Promise((resolve) => service.once("exit", resolve));
  void (async () => {
    try {
      await fetch(serviceOrigin + "/launcher/shutdown", {
        method: "POST",
        headers: {
          Authorization: "Bearer " + serviceToken,
          "X-KBW-Request": "v1",
          "Content-Type": "application/json",
        },
        body: "{}",
        signal: AbortSignal.timeout(2000),
      });
      await Promise.race([
        stopped,
        new Promise((resolve) => setTimeout(resolve, 30000)),
      ]);
    } catch {
      /* Parent monitor still requests graceful sealing if this launcher exits. */
    }
    app.exit(0);
  })();
});
app.on("window-all-closed", () => app.quit());
app.setPath(
  "userData",
  (process.env.KBW_DESKTOP_TEST && process.env.KBW_TEST_LAUNCHER_DATA) ||
    join(app.getPath("appData"), "BusinessKnowledgeWorkbenchLauncher"),
);
if (!app.requestSingleInstanceLock()) app.quit();
else {
  app.on("second-instance", () => {
    const window = BrowserWindow.getAllWindows()[0];
    if (window) {
      window.restore();
      window.focus();
    }
  });
  app
    .whenReady()
    .then(launch)
    .catch((error) => {
      if (process.env.KBW_DESKTOP_TEST) console.error(error.message);
      else dialog.showErrorBox("Workbench startup", error.message);
      app.quit();
    });
}
