/* @index-begin
 * @symbol function/class: libraryJourney L26
 * @symbol variable/parameter: page L27
 * @symbol variable/parameter: audit L28
 * @symbol variable/parameter: downloadBundle L29
 * @symbol variable/parameter: file L31
 * @symbol variable/parameter: preview L99
 * @symbol variable/parameter: link L157
 * @symbol variable/parameter: href L161
 * @symbol variable/parameter: output L162
 * @symbol variable/parameter: url L162
 * @symbol variable/parameter: response L163
 * @symbol variable/parameter: bytes L164
 * @symbol variable/parameter: bundle L174
 * @symbol variable/parameter: downloaded L194
 * @symbol variable/parameter: download L196
@index-end */
/** Jason Stys: visible field-edit, file-preview, import, filtered-search and download regression.
 * Functions/variables and exact lines: docs/code-index.md. All records are fictional.
 */
import { expect, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { readFileSync } from "node:fs";

/** Exercise the same authenticated workflow in real browsers and packaged native renderers. */
export async function libraryJourney(
  page: Page,
  audit = true,
  downloadBundle?: () => Promise<Uint8Array>,
): Promise<void> {
  const file = {
    name: "fictional-inspection.csv",
    mimeType: "text/csv",
    buffer: Buffer.from(
      "part,width,note,obsolete\nPanel A,4.25 in,Internal supplier note,old code\nBracket B,8.2 cm,Internal batch note,old code",
    ),
  };
  await page
    .getByRole("button", { name: "Configuration studio", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Use measurement-table example" })
    .click();
  await page
    .getByRole("button", { name: "Add standard field", exact: true })
    .click();
  await page.getByLabel("Field key 3", { exact: true }).fill("note");
  await page.getByLabel("Field label 3", { exact: true }).fill("Supplier note");
  await page
    .getByRole("button", { name: "Move field 3 up", exact: true })
    .click();
  await expect(page.getByLabel("Field key 2", { exact: true })).toHaveValue(
    "note",
  );
  await page
    .getByRole("button", { name: "Move field 2 down", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Add standard field", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Remove field 4", exact: true })
    .click();
  await expect(page.locator("[data-field-row]")).toHaveCount(3);
  await page.getByLabel("Include field 3 in output", { exact: true }).uncheck();
  await page
    .getByRole("combobox", { name: "Extra table columns", exact: true })
    .selectOption("omit");
  await page
    .getByRole("combobox", { name: "Standard export type", exact: true })
    .selectOption("docx");
  await page.getByLabel("Page margins (mm)", { exact: true }).fill("25");
  await page
    .getByRole("combobox", { name: "Paragraph alignment", exact: true })
    .selectOption("right");
  await page
    .getByRole("combobox", { name: "Line spacing", exact: true })
    .selectOption("1.5");
  await page
    .getByLabel("Running header", { exact: true })
    .fill("Fictional Harbor Manufacturing");
  await page
    .getByLabel("Running footer", { exact: true })
    .fill("Synthetic inspection report");
  await page
    .getByLabel("Include page numbers in DOCX and PDF", { exact: true })
    .check();
  await page
    .getByLabel("Optional file for draft preview", { exact: true })
    .setInputFiles(file);
  if (audit)
    expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await page
    .getByRole("button", { name: "Preview draft standard", exact: true })
    .click();
  await expect(page.locator("#standard-preview-status")).toContainText(
    "not saved",
  );
  const preview = page.frameLocator("#standard-preview-frame");
  await expect(preview.getByText("107.95 mm", { exact: true })).toBeVisible();
  await expect(
    preview.getByText("Internal supplier note", { exact: true }),
  ).toHaveCount(0);
  await expect(
    preview.getByText("Fictional Harbor Manufacturing", { exact: true }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Save validated configuration", exact: true })
    .click();
  await expect(page.locator("#notice")).toContainText("Configuration saved");
  await page
    .getByRole("button", { name: "Business workspace", exact: true })
    .click();
  // A draft preview must not create a stored document.
  await expect(
    page.getByRole("button", {
      name: "Preview fictional-inspection.csv",
      exact: true,
    }),
  ).toHaveCount(0);
  await page.getByLabel("Source file", { exact: true }).setInputFiles(file);
  await page
    .getByRole("button", { name: "Import & standardize", exact: true })
    .click();
  await expect(page.locator("#preview h3")).toContainText(file.name);
  await page.getByLabel("Search documents", { exact: true }).fill(file.name);
  await page
    .getByRole("combobox", { name: "Source file type", exact: true })
    .selectOption("csv");
  await page
    .getByRole("combobox", { name: "Data type", exact: true })
    .selectOption("table");
  await page
    .getByRole("combobox", { name: "Measurement type", exact: true })
    .selectOption("length");
  await page
    .getByRole("combobox", { name: "Table field", exact: true })
    .fill("width");
  await page.getByLabel("Field contains", { exact: true }).fill("107.95 mm");
  await page.getByLabel("Minimum (inclusive)", { exact: true }).fill("10");
  await page.getByLabel("Maximum (inclusive)", { exact: true }).fill("11");
  await page
    .getByRole("combobox", { name: "Numeric comparison unit", exact: true })
    .selectOption("cm");
  await page
    .getByRole("button", { name: "Apply filters", exact: true })
    .click();
  await expect(page.locator("#documents [role=status]")).toContainText(
    "of 1 permitted files",
  );
  await expect(
    page.getByRole("button", { name: "Previous files", exact: true }),
  ).toBeDisabled();
  await expect(
    page.getByRole("button", { name: "Next files", exact: true }),
  ).toBeDisabled();
  const link = page.getByRole("link", {
    name: "Download standardized fictional-inspection.csv",
    exact: true,
  });
  const href = new URL((await link.getAttribute("href"))!, page.url()).href;
  const output = await page.evaluate(async (url) => {
    const response = await fetch(url);
    const bytes = new Uint8Array(await response.arrayBuffer());
    return {
      status: response.status,
      prefix: [...bytes.slice(0, 2)],
      size: bytes.length,
    };
  }, href);
  expect(output.status).toBe(200);
  expect(output.prefix).toEqual([80, 75]);
  expect(output.size).toBeGreaterThan(1000);
  const bundle = page.getByRole("button", {
    name: "Download selected files (ZIP)",
    exact: true,
  });
  await expect(bundle).toBeDisabled();
  await page
    .getByRole("checkbox", {
      name: "Select fictional-inspection.csv",
      exact: true,
    })
    .check();
  await expect(bundle).toBeEnabled();
  await expect(page.locator("#bundle-count")).toContainText("1 selected");
  if (downloadBundle) {
    const bytes = await downloadBundle();
    expect([...bytes.subarray(0, 2)]).toEqual([80, 75]);
    expect(bytes.length).toBeGreaterThan(1000);
  } else if (audit) {
    // Browser downloads are real files; packaged native download plumbing has its
    // own existing will-download test rather than a simulated anchor-click stub.
    const downloaded = page.waitForEvent("download");
    await bundle.click();
    const download = await downloaded;
    expect(download.suggestedFilename()).toBe("standardized-documents.zip");
    const bytes = readFileSync((await download.path())!);
    expect([...bytes.subarray(0, 2)]).toEqual([80, 75]);
    expect(bytes.length).toBeGreaterThan(1000);
  }
  await page
    .getByRole("button", { name: "Clear selection", exact: true })
    .click();
  await expect(bundle).toBeDisabled();
  await expect(page.locator("#bundle-count")).toContainText("0 selected");
  await page
    .getByRole("combobox", { name: "Table field", exact: true })
    .fill("item");
  await page
    .getByRole("button", { name: "Apply filters", exact: true })
    .click();
  await expect(page.locator("#documents [role=status]")).toContainText(
    "of 0 permitted files",
  );
  await page
    .getByRole("button", { name: "Clear filters", exact: true })
    .click();
  await expect(link).toBeVisible();
  // Close the real preview through its public control. Axe cannot inspect an
  // opaque-origin scriptless frame; the library itself is audited in full.
  await page
    .getByRole("button", { name: "Close document preview", exact: true })
    .click();
  await expect(page.locator("#preview iframe")).toHaveCount(0);
  if (audit) {
    await page.setViewportSize({ width: 390, height: 844 });
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBe(true);
    expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
    await page.setViewportSize({ width: 1280, height: 900 });
  }
}
