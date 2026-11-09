/* @index-begin
 * @symbol variable/parameter: temporary L29
 * @symbol variable/parameter: logs L30
 * @symbol variable/parameter: app L32
 * @symbol variable/parameter: page L43
 * @symbol variable/parameter: destination L47
 * @symbol variable/parameter: completed L48
 * @symbol variable/parameter: target L49
 * @symbol variable/parameter: { BrowserWindow } L49
 * @symbol variable/parameter: reject L51
 * @symbol variable/parameter: resolve L51
 * @symbol variable/parameter: timer L52
 * @symbol variable/parameter: _event L58
 * @symbol variable/parameter: item L58
 * @symbol variable/parameter: state L60
 * @symbol variable/parameter: data L74
 * @symbol variable/parameter: error L132
 * @symbol variable/parameter: log L133
@index-end */
/** Jason Stys: genuine packaged native application conversion, encrypted lock and renderer sandbox checks. */
import { test, expect, _electron as electron } from "@playwright/test";
import { mkdtempSync, readFileSync, mkdirSync, existsSync } from "node:fs";
import { join } from "node:path";
import { tmpdir } from "node:os";
import { createSession, documentJourney } from "./account-session";
import { standardJourney } from "./standard-journey";
import { libraryJourney } from "./library-journey";
test("native application imports rich documents with private accounts and no renderer privileges", async () => {
  const temporary = mkdtempSync(join(tmpdir(), "kbw-native-"));
  const logs = join(temporary, "launcher");
  mkdirSync(logs);
  const app = await electron.launch({
    executablePath: process.env.KBW_INSTALLED_APP,
    args: process.env.KBW_INSTALLED_APP ? [] : ["."],
    env: {
      ...process.env,
      KBW_DESKTOP_TEST: "1",
      KBW_TEST_LAUNCHER_DATA: logs,
      KBW_ACCOUNT_DATA: join(temporary, "accounts"),
    },
  });
  try {
    const page = await app.firstWindow();
    await page.waitForURL(/^http:\/\/127\.0\.0\.1:\d+\/$/);
    await createSession(page, "native_fictional");
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
    await libraryJourney(page, false, async () => {
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
    });
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
    await page.screenshot({
      path: "artifacts/native-workspace.png",
      fullPage: false,
    });
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
});
