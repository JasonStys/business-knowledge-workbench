/* @index-begin
 * @symbol variable/parameter: temporary L24
 * @symbol variable/parameter: app L25
 * @symbol variable/parameter: page L35
 * @symbol variable/parameter: destination L39
 * @symbol variable/parameter: completed L40
 * @symbol variable/parameter: target L41
 * @symbol variable/parameter: { BrowserWindow } L41
 * @symbol variable/parameter: reject L43
 * @symbol variable/parameter: resolve L43
 * @symbol variable/parameter: timer L44
 * @symbol variable/parameter: _event L50
 * @symbol variable/parameter: item L50
 * @symbol variable/parameter: state L52
 * @symbol variable/parameter: data L66
@index-end */
/** Jason Stys: genuine packaged native application conversion, encrypted lock and renderer sandbox checks. */
import { test, expect, _electron as electron } from "@playwright/test";
import { mkdtempSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { tmpdir } from "node:os";
import { createSession, documentJourney } from "./account-session";
test("native application imports rich documents with private accounts and no renderer privileges", async () => {
  const temporary = mkdtempSync(join(tmpdir(), "kbw-native-"));
  const app = await electron.launch({
    executablePath: process.env.KBW_INSTALLED_APP,
    args: process.env.KBW_INSTALLED_APP ? [] : ["."],
    env: {
      ...process.env,
      KBW_DESKTOP_TEST: "1",
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
      fullPage: true,
    });
    await page
      .getByRole("button", { name: "Lock workspace", exact: true })
      .click();
    await expect(
      page.getByRole("heading", {
        name: "Unlock your private business workspace",
      }),
    ).toBeVisible();
  } finally {
    await app.close();
  }
});
