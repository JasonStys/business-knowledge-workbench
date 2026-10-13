/* @index-begin
@index-end */
/** Jason Stys: real frozen Python/Electron integration, no service mock or separate runtime installation. */
import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "tests/browser",
  outputDir: "test-results/native",
  testMatch: "desktop.spec.ts",
  workers: 1,
  timeout: 90000,
  expect: { timeout: 15000 },
});
