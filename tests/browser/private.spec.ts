/* @index-begin
 * @symbol variable/parameter: { page } L20
 * @symbol variable/parameter: { page, } L32
 * @symbol variable/parameter: info L34
 * @symbol variable/parameter: external L35
 * @symbol variable/parameter: request L36
 * @symbol variable/parameter: { page, request, } L74
 * @symbol variable/parameter: denied L87
 * @symbol variable/parameter: release L98
 * @symbol variable/parameter: delayed L99
 * @symbol variable/parameter: resolve L99
 * @symbol variable/parameter: route L102
 * @symbol variable/parameter: releaseLibrary L118
 * @symbol variable/parameter: library L119
@index-end */
/** Jason Stys: private website workflow, hostile origins, account isolation and responsive accessibility. */
import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { createSession, documentJourney, phrase } from "./account-session";
test.afterEach(async ({ page }) => {
  await page
    .evaluate(async () => {
      await fetch("/private/lock", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-KBW-Request": "v1" },
        body: "{}",
      });
    })
    .catch(() => {});
});

test("private documents convert, export, seal and reopen without external requests", async ({
  page,
}, info) => {
  const external: string[] = [];
  page.on("request", (request) => {
    if (
      request.url().startsWith("http") &&
      new URL(request.url()).origin !== "http://127.0.0.1:8078"
    )
      external.push(request.url());
  });
  await createSession(page, "fictional_" + info.project.name);
  await documentJourney(page);
  expect(
    await page.evaluate(() => localStorage.length + sessionStorage.length),
  ).toBe(0);
  expect(await page.evaluate(() => document.cookie)).not.toContain(
    "kbw_account",
  );
  expect(external).toEqual([]);
  await page
    .getByRole("button", { name: "Lock workspace", exact: true })
    .click();
  await expect(
    page.getByRole("heading", {
      name: "Unlock your private business workspace",
    }),
  ).toBeVisible();
  await page.getByLabel("Vault phrase", { exact: true }).fill(phrase);
  await page
    .getByRole("button", { name: "Unlock workspace", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Business workspace", exact: true })
    .click();
  await expect(page.locator("#documents tbody tr")).toHaveCount(10);
  await page.getByRole("button", { name: "Sign out", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Create your local account" }),
  ).toBeVisible();
});

test("account form is accessible on small screens and rejects cross-origin mutations", async ({
  page,
  request,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await page.getByText("Privacy and setup help", { exact: true }).click();
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  const denied = await request.post("/private/register", {
    headers: { Origin: "https://evil.example", "X-KBW-Request": "v1" },
    data: { alias: "cross_origin", password: "fictional-login-only" },
  });
  expect(denied.status()).toBe(403);
  expect((await request.get("/private/api/documents")).status()).toBe(401);
});

test("delayed initial view cannot overwrite a newly selected workspace", async ({
  page,
}, info) => {
  let release: () => void = () => {};
  const delayed = new Promise<void>((resolve) => {
    release = resolve;
  });
  await page.route("**/private/api/audit*", async (route) => {
    await delayed;
    await route.continue();
  });
  try {
    await createSession(page, "delayed_" + info.project.name);
    await expect(
      page.getByRole("button", { name: "Business workspace", exact: true }),
    ).toBeDisabled();
    await expect(
      page.getByRole("button", { name: "Account, AI & help" }),
    ).toBeDisabled();
    release();
    await expect(
      page.getByRole("button", { name: "Business workspace", exact: true }),
    ).toBeEnabled();
    let releaseLibrary: () => void = () => {};
    const library = new Promise<void>((resolve) => {
      releaseLibrary = resolve;
    });
    await page.route(/\/private\/api\/documents\?/, async (route) => {
      await library;
      await route.continue();
    });
    try {
      await page
        .getByRole("button", { name: "Business workspace", exact: true })
        .click();
      await expect(
        page.getByRole("button", { name: "Import & standardize", exact: true }),
      ).toBeDisabled();
    } finally {
      releaseLibrary();
    }
    await expect(
      page.getByRole("button", { name: "Import & standardize", exact: true }),
    ).toBeEnabled();
    await documentJourney(page);
    await page
      .getByRole("button", { name: "Lock workspace", exact: true })
      .click();
    await expect(
      page.getByRole("heading", {
        name: "Unlock your private business workspace",
      }),
    ).toBeVisible();
  } finally {
    release();
  }
});
