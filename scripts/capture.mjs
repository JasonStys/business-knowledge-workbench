/* @index-begin
 * @symbol variable/parameter: browser L9
 * @symbol variable/parameter: page L11
@index-end */
/** Capture synthetic desktop/mobile UI evidence against the local preview. Index: docs/code-index.md. */
import { chromium } from "@playwright/test";
import { mkdir } from "node:fs/promises";
await mkdir("docs/screenshots", { recursive: true });
const browser = await chromium.launch();
try {
  const page = await browser.newPage({
    viewport: { width: 1440, height: 1100 },
  });
  await page.goto("http://127.0.0.1:8001");
  await page.locator(".product-card").first().waitFor();
  await page.screenshot({
    path: "docs/screenshots/catalog.png",
    fullPage: true,
  });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.screenshot({
    path: "docs/screenshots/mobile.png",
    fullPage: true,
  });
  await page.setViewportSize({ width: 1440, height: 1100 });
  await page
    .getByRole("button", { name: "Business workspace", exact: true })
    .click();
  await page.getByLabel("Password", { exact: true }).fill("workbench-demo");
  await page.getByRole("button", { name: "Sign in securely" }).click();
  await page.locator(".chart").waitFor();
  await page.screenshot({
    path: "docs/screenshots/workspace.png",
    fullPage: true,
  });
} finally {
  await browser.close();
}
