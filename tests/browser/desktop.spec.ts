/* @index-begin
 * @symbol variable/parameter: temporary L39
 * @symbol variable/parameter: logs L40
 * @symbol variable/parameter: launch L42
 * @symbol variable/parameter: app L53
 * @symbol variable/parameter: retainedRows L54
 * @symbol variable/parameter: { app } L56
 * @symbol variable/parameter: page L59
 * @symbol variable/parameter: health L61
 * @symbol variable/parameter: destination L66
 * @symbol variable/parameter: completed L67
 * @symbol variable/parameter: target L68
 * @symbol variable/parameter: { BrowserWindow } L68
 * @symbol variable/parameter: reject L70
 * @symbol variable/parameter: resolve L70
 * @symbol variable/parameter: timer L71
 * @symbol variable/parameter: _event L77
 * @symbol variable/parameter: item L77
 * @symbol variable/parameter: state L79
 * @symbol variable/parameter: data L93
 * @symbol variable/parameter: error L166
 * @symbol variable/parameter: log L167
 * @symbol variable/parameter: reopened L179
@index-end */
/** Jason Stys: genuine packaged native application conversion, encrypted lock and renderer sandbox checks. */
import { test, expect, _electron as electron } from "@playwright/test";
import { mkdtempSync, readFileSync, mkdirSync, existsSync } from "node:fs";
import { join } from "node:path";
import { tmpdir } from "node:os";
import {
  createSession,
  documentJourney,
  phrase,
  verifyCatalogSymbols,
} from "./account-session";
import { standardJourney } from "./standard-journey";
import { libraryJourney } from "./library-journey";
test("native application imports rich documents with private accounts and no renderer privileges", async () => {
  const temporary = mkdtempSync(join(tmpdir(), "kbw-native-"));
  const logs = join(temporary, "launcher");
  mkdirSync(logs);
  const launch = () =>
    electron.launch({
      executablePath: process.env.KBW_INSTALLED_APP,
      args: process.env.KBW_INSTALLED_APP ? [] : ["."],
      env: {
        ...process.env,
        KBW_DESKTOP_TEST: "1",
        KBW_TEST_LAUNCHER_DATA: logs,
        KBW_ACCOUNT_DATA: join(temporary, "accounts"),
      },
    });
  const app = await launch();
  let retainedRows: string[] = [];
  try {
    expect(await app.evaluate(({ app }) => app.getVersion())).toBe(
      JSON.parse(readFileSync("package.json", "utf8")).version,
    );
    const page = await app.firstWindow();
    await page.waitForURL(/^http:\/\/127\.0\.0\.1:\d+\/$/);
    const health = await page.request.get(new URL("/health", page.url()).href);
    expect((await health.json()).runtime_python).toBe("3.14.10");
    await createSession(page, "native_fictional");
    await verifyCatalogSymbols(page);
    await documentJourney(page, async () => {
      const destination = join(temporary, "document.json");
      const completed = app.evaluate(
        async ({ BrowserWindow }, target) =>
          new Promise<{ state: string; filename: string }>(
            (resolve, reject) => {
              const timer = setTimeout(
                () => reject(new Error("Native export did not finish")),
                30000,
              );
              BrowserWindow.getAllWindows()[0]!.webContents.session.once(
                "will-download",
                (_event, item) => {
                  item.setSavePath(target);
                  item.once("done", (_event, state) => {
                    clearTimeout(timer);
                    resolve({ state, filename: item.getFilename() });
                  });
                },
              );
            },
          ),
        destination,
      );
      await page
        .getByRole("link", { name: "Export JSON", exact: true })
        .click();
      expect((await completed).state).toBe("completed");
      const data = JSON.parse(readFileSync(destination, "utf8"));
      expect(data.blocks.length).toBeGreaterThan(0);
      expect(data.provenance.conversion_path).toEqual(["docx", "html"]);
    });
    await standardJourney(page, false);
    await libraryJourney(
      page,
      false,
      async () => {
        const destination = join(temporary, "standardized-documents.zip");
        const completed = app.evaluate(
          async ({ BrowserWindow }, target) =>
            new Promise<string>((resolve, reject) => {
              const timer = setTimeout(
                () => reject(new Error("Native bundle did not finish")),
                30000,
              );
              BrowserWindow.getAllWindows()[0]!.webContents.session.once(
                "will-download",
                (_event, item) => {
                  item.setSavePath(target);
                  item.once("done", (_event, state) => {
                    clearTimeout(timer);
                    resolve(state);
                  });
                },
              );
            }),
          destination,
        );
        await page
          .getByRole("button", {
            name: "Download selected files (ZIP)",
            exact: true,
          })
          .click();
        expect(await completed).toBe("completed");
        return readFileSync(destination);
      },
      async () => {
        await page
          .frameLocator("#standard-preview-frame")
          .locator("body")
          .screenshot({
            path: "artifacts/native-standard-preview.png",
          });
      },
    );
    expect(
      await page.evaluate(
        () => typeof (window as unknown as { require?: unknown }).require,
      ),
    ).toBe("undefined");
    expect(
      await page.evaluate(
        () => typeof (window as unknown as { process?: unknown }).process,
      ),
    ).toBe("undefined");
    await page.getByRole("heading", { level: 1 }).scrollIntoViewIfNeeded();
    await page.screenshot({
      path: "artifacts/native-workspace.png",
      fullPage: false,
    });
    retainedRows = await page.locator("#documents tbody tr").allTextContents();
    expect(retainedRows.length).toBeGreaterThan(0);
    await page
      .getByRole("button", { name: "Lock workspace", exact: true })
      .click();
    await expect(
      page.getByRole("heading", {
        name: "Unlock your private business workspace",
      }),
    ).toBeVisible();
  } catch (error) {
    const log = join(logs, "service.log");
    if (existsSync(log))
      console.error(
        "Disposable native service diagnostic:",
        readFileSync(log, "utf8").slice(-24000),
      );
    throw error;
  } finally {
    await app.close();
  }
  // Relaunch the compiled app against the same synthetic account, not a rebuilt
  // source server. Authentication and vault decryption must both work again.
  const reopened = await launch();
  try {
    const page = await reopened.firstWindow();
    await page.waitForURL(/^http:\/\/127\.0\.0\.1:\d+\/$/);
    await page
      .getByRole("button", { name: "Sign in instead", exact: true })
      .click();
    await page
      .getByLabel("Account alias", { exact: true })
      .fill("native_fictional");
    await page
      .getByLabel("Login password", { exact: true })
      .fill("synthetic-only-login-password-2026");
    await page.getByRole("button", { name: "Sign in", exact: true }).click();
    await page.getByLabel("Vault phrase", { exact: true }).fill(phrase);
    await page
      .getByRole("button", { name: "Unlock workspace", exact: true })
      .click();
    await page
      .getByRole("button", { name: "Business workspace", exact: true })
      .click();
    await expect(page.locator("#documents tbody tr")).toHaveCount(
      retainedRows.length,
    );
    expect(await page.locator("#documents tbody tr").allTextContents()).toEqual(
      retainedRows,
    );
    await page
      .getByRole("button", { name: "Lock workspace", exact: true })
      .click();
    await expect(
      page.getByRole("heading", {
        name: "Unlock your private business workspace",
      }),
    ).toBeVisible();
  } finally {
    await reopened.close();
  }
});
