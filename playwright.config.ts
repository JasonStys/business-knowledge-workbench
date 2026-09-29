/* @index-begin
 * @symbol variable/parameter: python L8
@index-end */
/** Browser matrix, isolated demo service and test artifacts. Index: docs/code-index.md. */
import { defineConfig, devices } from "@playwright/test";
import { existsSync } from "node:fs";
import { resolve } from "node:path";
const python = existsSync(".venv/Scripts/python.exe")
  ? `"${resolve(".venv/Scripts/python.exe")}"`
  : "python";
export default defineConfig({
  testDir: "tests/browser",
  timeout: 45000,
  expect: { timeout: 10000 },
  fullyParallel: false,
  workers: 1,
  retries: process.env.CI ? 1 : 0,
  reporter: [
    ["list"],
    ["json", { outputFile: "docs/reports/browser-results.json" }],
    ["html", { open: "never" }],
  ],
  use: {
    baseURL: "http://127.0.0.1:8000",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
    { name: "firefox", use: { ...devices["Desktop Firefox"] } },
    { name: "webkit", use: { ...devices["Desktop Safari"] } },
    {
      name: "mobile",
      use: { ...devices["iPhone 13"], defaultBrowserType: "chromium" },
    },
  ],
  webServer: {
    command: `${python} -m uvicorn server.app:app --host 127.0.0.1 --port 8000`,
    url: "http://127.0.0.1:8000/api/health",
    reuseExistingServer: false,
    timeout: 45000,
    env: {
      KB_DEMO: "1",
      KB_DB: `data/browser-${Date.now()}.sqlite`,
      KB_LOGIN_LIMIT: "100",
    },
  },
});
