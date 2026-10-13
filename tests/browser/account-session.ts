/* @index-begin
 * @symbol variable/parameter: phrase L13
 * @symbol variable/parameter: alias L15
 * @symbol function/class: createSession L15
 * @symbol variable/parameter: page L15
 * @symbol function/class: documentJourney L43
 * @symbol variable/parameter: verifyNativeDownload L45
 * @symbol variable/parameter: downloaded L66
@index-end */
/** Jason Stys: reusable genuine registration, encryption and rich import journey; fictional credentials only. */
import { expect, type Page } from "@playwright/test";

export const phrase = "synthetic-only-independent-vault-phrase-2026";
/** Drive visible account forms, never skipping authentication or WebCrypto. */
export async function createSession(page: Page, alias: string): Promise<void> {
  await page.goto(
    page.url().startsWith("http://127.0.0.1:")
      ? new URL("/", page.url()).href
      : "/",
  );
  await page.getByLabel("Account alias", { exact: true }).fill(alias);
  await page
    .getByLabel("Login password", { exact: true })
    .fill("synthetic-only-login-password-2026");
  await page
    .getByRole("button", { name: "Create account", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Save your recovery code" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "I saved my recovery code" }).click();
  await page.getByLabel("Vault phrase", { exact: true }).fill(phrase);
  await page.getByLabel("Confirm vault phrase", { exact: true }).fill(phrase);
  await page
    .getByRole("button", { name: "Unlock workspace", exact: true })
    .click();
  await expect(
    page.getByRole("button", { name: "Account, AI & help" }),
  ).toBeVisible();
}

/** Import actual DOCX with figures/table/equation, preview, export, save and test seeded reporting. */
export async function documentJourney(
  page: Page,
  verifyNativeDownload?: () => Promise<void>,
): Promise<void> {
  await page
    .getByRole("button", { name: "Business workspace", exact: true })
    .click();
  await page
    .getByLabel("Source file", { exact: true })
    .setInputFiles("examples/commissioning-pack.docx");
  await page
    .getByRole("button", { name: "Import & standardize", exact: true })
    .click();
  await expect(page.locator("#preview h3")).toContainText(
    "commissioning-pack.docx",
  );
  await expect(
    page
      .frameLocator("iframe")
      .getByRole("heading", { name: "Content", exact: true }),
  ).toBeVisible();
  if (verifyNativeDownload) await verifyNativeDownload();
  else {
    const downloaded = page.waitForEvent("download");
    await page.getByRole("link", { name: "Export JSON", exact: true }).click();
    expect((await downloaded).suggestedFilename()).toMatch(/\.json$/);
  }
  await page.getByRole("button", { name: "Account, AI & help" }).click();
  await page.getByRole("button", { name: "Load synthetic examples" }).click();
  await expect(page.locator("#account-status")).toContainText(
    "Synthetic examples added",
  );
  await page.getByRole("button", { name: "Save encrypted snapshot" }).click();
  await expect(page.locator("#account-status")).toContainText(
    "Encrypted snapshot saved",
  );
  await page
    .getByRole("button", { name: "Business workspace", exact: true })
    .click();
  await expect(page.getByText("No sales data yet.")).toHaveCount(0);
  await expect(page.locator("#documents tbody tr")).toHaveCount(10);
}
