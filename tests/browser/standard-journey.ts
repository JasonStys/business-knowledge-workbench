/* @index-begin
 * @symbol function/class: ownResponse L22
 * @symbol variable/parameter: page L23
 * @symbol variable/parameter: url L24
 * @symbol variable/parameter: target L26
 * @symbol variable/parameter: response L27
 * @symbol function/class: standardJourney L33
 * @symbol variable/parameter: checkAccessibility L35
 * @symbol variable/parameter: link L110
 * @symbol variable/parameter: href L114
 * @symbol variable/parameter: output L115
 * @symbol variable/parameter: before L118
 * @symbol variable/parameter: original L141
@index-end */
/** Jason Stys: real draft/publish/import/export/re-standardize/restore journey shared by browser and native tests.
 * Functions/variables and exact lines: docs/code-index.md. Fictional fixture records only.
 */
import { expect, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

/** Use the rendered app's genuine HttpOnly-cookie session, including Electron's separate cookie partition. */
async function ownResponse(
  page: Page,
  url: string,
): Promise<{ status: number; body: string }> {
  return page.evaluate(async (target) => {
    const response = await fetch(target, { credentials: "same-origin" });
    return { status: response.status, body: await response.text() };
  }, url);
}

/** Exercise visible standards controls and actual exported bytes without opening OS save dialogs. */
export async function standardJourney(
  page: Page,
  checkAccessibility = true,
): Promise<void> {
  await page
    .getByRole("button", { name: "Configuration studio", exact: true })
    .click();
  await page
    .getByLabel("Standard name", { exact: true })
    .fill("Fictional metric manufacturing");
  await page
    .getByRole("combobox", { name: "Standard export type", exact: true })
    .selectOption("pdf");
  await page
    .getByRole("combobox", { name: "Paper size", exact: true })
    .selectOption("A4");
  await page
    .getByRole("combobox", { name: "Page orientation", exact: true })
    .selectOption("landscape");
  await page
    .getByLabel("Restrict document/report exports to the standard file type")
    .check();
  await page
    .getByRole("button", { name: "Use measurement-table example" })
    .click();
  // Audit the complete owner form before activating a scriptless opaque-origin
  // preview. Browser engines cover accessibility; Electron cannot create axe's
  // auxiliary browser context and is tested separately for the actual workflow.
  if (checkAccessibility)
    expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await page.getByRole("button", { name: "Preview draft standard" }).click();
  await expect(page.locator("#standard-preview-status")).toContainText(
    "not saved",
  );
  await expect(
    page
      .frameLocator("#standard-preview-frame")
      .getByText("107.95 mm", { exact: true }),
  ).toBeVisible();
  // Chromium/Firefox/WebKit emulate mobile viewports. A real Electron window
  // retains its OS-managed size; CDP viewport emulation can stall native capture.
  if (checkAccessibility)
    await page.setViewportSize({ width: 390, height: 844 });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  if (checkAccessibility)
    await page.setViewportSize({ width: 1280, height: 900 });
  await page
    .getByRole("button", { name: "Save validated configuration", exact: true })
    .click();
  await expect(page.locator("#notice")).toContainText("Configuration saved");
  await expect(page.getByLabel("Standard name", { exact: true })).toHaveValue(
    "Fictional metric manufacturing",
  );
  await page
    .getByRole("button", { name: "Business workspace", exact: true })
    .click();
  await expect(
    page.getByRole("link", { name: "Download standard report PDF" }),
  ).toBeVisible();
  await page.getByLabel("Source file", { exact: true }).setInputFiles({
    name: "standard-fixture.csv",
    mimeType: "text/csv",
    buffer: Buffer.from("width,item\n4.25 in,Panel\n8.2 cm,Bracket"),
  });
  await page
    .getByRole("button", { name: "Import & standardize", exact: true })
    .click();
  await expect(
    page.frameLocator("iframe").getByText("107.95 mm", { exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("link", { name: "Export JSON", exact: true }),
  ).toHaveCount(0);
  const link = page.getByRole("link", {
    name: "Download standard PDF",
    exact: true,
  });
  const href = new URL((await link.getAttribute("href"))!, page.url()).href;
  const output = await ownResponse(page, href);
  expect(output.status).toBe(200);
  expect(output.body.slice(0, 4)).toBe("%PDF");
  const before = href.replace("/export/pdf", "");
  await page
    .getByRole("button", { name: "Configuration studio", exact: true })
    .click();
  await page
    .getByRole("combobox", { name: "length target", exact: true })
    .selectOption("cm");
  await page
    .getByRole("button", { name: "Save validated configuration", exact: true })
    .click();
  await expect(page.locator("#notice")).toContainText("Configuration saved");
  await page
    .getByRole("button", { name: "Business workspace", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Preview standard-fixture.csv", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Create current-standard copy" })
    .click();
  await expect(
    page.frameLocator("iframe").getByText("10.795 cm", { exact: true }),
  ).toBeVisible();
  const original = await ownResponse(page, before);
  expect(original.status).toBe(200);
  expect(JSON.parse(original.body).blocks[0].rows[1]).toEqual([
    "Panel",
    "107.95 mm",
  ]);
  await page
    .getByRole("button", { name: "Configuration studio", exact: true })
    .click();
  await page
    .getByRole("combobox", { name: "Revision to restore", exact: true })
    .selectOption("1");
  await page.getByRole("button", { name: "Restore as new revision" }).click();
  await expect(page.locator("#notice")).toContainText(
    "restored as a new revision",
  );
  await expect(page.getByLabel("Standard name", { exact: true })).toHaveValue(
    "Business standard",
  );
}
