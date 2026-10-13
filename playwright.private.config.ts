/* @index-begin
 * @symbol variable/parameter: python L9
@index-end */
/** Jason Stys: isolated private service and three genuine browser engines; no credential traces. */
import { defineConfig, devices } from "@playwright/test";
import { existsSync, mkdtempSync } from "node:fs";
import { resolve, join } from "node:path";
import { tmpdir } from "node:os";
const python = existsSync(".venv/Scripts/python.exe")
  ? `"${resolve(".venv/Scripts/python.exe")}"`
  : "python";
export default defineConfig({
  testDir: "tests/browser",
  outputDir: "test-results/private",
  testMatch: "private.spec.ts",
  workers: 1,
  timeout: 60000,
  expect: { timeout: 15000 },
  use: { baseURL: "http://127.0.0.1:8078", trace: "off" },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
    { name: "firefox", use: { ...devices["Desktop Firefox"] } },
    { name: "webkit", use: { ...devices["Desktop Safari"] } },
  ],
  webServer: {
    command: `${python} -m server.private_cli --port 8078 --no-browser`,
    url: "http://127.0.0.1:8078/health",
    reuseExistingServer: false,
    env: { KBW_ACCOUNT_DATA: mkdtempSync(join(tmpdir(), "kbw-private-web-")) },
  },
});
