/* @index-begin
 * @symbol function/class: login L27
 * @symbol variable/parameter: page L27
 * @symbol variable/parameter: role L27
 * @symbol variable/parameter: { page, } L45
 * @symbol variable/parameter: download L76
 * @symbol variable/parameter: denied L107
 * @symbol variable/parameter: testInfo L113
 * @symbol variable/parameter: name L116
 * @symbol variable/parameter: { page, browserName, } L189
 * @symbol variable/parameter: results L195
 * @symbol variable/parameter: { page, request, } L224
 * @symbol variable/parameter: manifest L229
 * @symbol variable/parameter: body L230
 * @symbol variable/parameter: select L250
 * @symbol variable/parameter: option L251
 * @symbol variable/parameter: cached L269
 * @symbol variable/parameter: names L270
 * @symbol variable/parameter: item L274
 * @symbol variable/parameter: url L280
@index-end */
/** Cross-browser workflow, accessibility, hostile input and PWA checks. Index: docs/code-index.md. */
import { test, expect, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

/** Sign in through the same visible form used by normal users. */
async function login(page: Page, role: string): Promise<void> {
  await page
    .getByRole("button", {
      name:
        role === "admin"
          ? "Configuration studio"
          : role === "employee"
            ? "Business workspace"
            : "Customer portal",
      exact: true,
    })
    .click();
  await page.getByLabel("Username", { exact: true }).fill(role);
  await page.getByLabel("Password", { exact: true }).fill("workbench-demo");
  await page.getByRole("button", { name: "Sign in securely" }).click();
  await expect(page.getByRole("button", { name: "Sign out" })).toBeVisible();
}

test("catalog, search, normalized units and canonical previews", async ({
  page,
}) => {
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: "Find the right product." }),
  ).toBeVisible();
  await expect(page.locator(".product-card")).toHaveCount(3);
  await page.getByLabel("Search catalog").fill("IO-16");
  await expect(page.locator(".product-card")).toHaveCount(1);
  await page.getByLabel("Search catalog").fill("not-a-product");
  await expect(page.getByText("No matching products.")).toBeVisible();
  await page.getByLabel("Value", { exact: true }).fill("2");
  await page.getByRole("button", { name: "Convert", exact: true }).click();
  await expect(page.locator("#unit-result")).toHaveText("2 in = 50.8 mm");
  await page
    .getByRole("combobox", { name: "To", exact: true })
    .selectOption("kg");
  await page.getByRole("button", { name: "Convert", exact: true }).click();
  await expect(page.locator("#notice")).toContainText(
    "incompatible dimensions",
  );
  await page
    .getByRole("button", { name: "Preview MC-240-overview.txt" })
    .click();
  await expect(
    page
      .frameLocator("iframe")
      .getByText("107.95 mm", { exact: false })
      .first(),
  ).toBeVisible();
  const download = page.waitForEvent("download");
  await page.getByRole("link", { name: "Export JSON", exact: true }).click();
  expect((await download).suggestedFilename()).toMatch(/\.json$/);
});

test("customer scope, reporting, safe AI opt-out and staff denial", async ({
  page,
}) => {
  await page.goto("/");
  await login(page, "customer");
  await expect(
    page.getByRole("heading", { name: "Your products. Your perspective." }),
  ).toBeVisible();
  await expect(
    page.getByText("PS-24-service.txt", { exact: true }),
  ).toHaveCount(0);
  await expect(
    page.getByRole("button", { name: "Import & standardize" }),
  ).toHaveCount(0);
  await page
    .getByLabel("Question", { exact: true })
    .fill("controller specifications");
  // Another admin may enable the shared reference profile; reset the scenario in the admin test afterward.
  await page.getByRole("button", { name: "Ask sources" }).click();
  await expect(page.locator("#notice")).toContainText("AI disabled");
  await page
    .getByRole("button", { name: "Configuration studio", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "This view requires a different role." }),
  ).toBeVisible();
  const denied = await page.request.get("/api/config");
  expect(denied.status()).toBe(403);
});

test("staff imports, HTML-first exports, selections and restricted compilation", async ({
  page,
}, testInfo) => {
  await page.goto("/");
  await login(page, "employee");
  const name = `synthetic-${testInfo.project.name}.csv`;
  await page.getByLabel("Source file").setInputFiles({
    name,
    mimeType: "text/csv",
    buffer: Buffer.from("part,width\nA,2 in\nB,3 cm"),
  });
  await page.getByRole("button", { name: "Import & standardize" }).click();
  await expect(page.getByRole("status")).toContainText(
    /Source converted|already imported/,
  );
  await expect(
    page
      .frameLocator("iframe")
      .getByRole("cell", { name: "50.8 mm", exact: true }),
  ).toBeVisible();
  await page
    .getByRole("checkbox", { name: `Select ${name}`, exact: true })
    .check();
  await page
    .getByRole("checkbox", { name: "Select MC-240-overview.txt", exact: true })
    .check();
  await page
    .getByLabel("Compilation title")
    .fill(`Evidence ${testInfo.project.name}`);
  await page
    .getByRole("button", { name: "Combine selected documents" })
    .click();
  await expect(page.getByRole("status")).toContainText(
    "Compilation created as internal-only",
  );
  await expect(
    page.frameLocator("iframe").getByRole("heading", {
      name: `Evidence ${testInfo.project.name}`,
      exact: true,
    }),
  ).toBeVisible();
});

test("admin config revisions, section ordering and grounded AI", async ({
  page,
}) => {
  await page.goto("/");
  await login(page, "admin");
  await expect(
    page.getByRole("heading", { name: "Adapt the workbench." }),
  ).toBeVisible();
  await page
    .getByLabel("Document section order")
    .fill("content, measurements, provenance, overview");
  await page.getByLabel("Enable read-only AI").check();
  await page
    .getByRole("button", { name: "Save validated configuration" })
    .click();
  await expect(page.getByRole("status")).toContainText("Configuration saved");
  await page
    .getByRole("button", { name: "Business workspace", exact: true })
    .click();
  await page
    .getByLabel("Question", { exact: true })
    .fill("MC-240 controller width");
  await page.getByRole("button", { name: "Ask sources" }).click();
  await expect(page.locator("#answer")).toContainText("extractive");
  await expect(page.locator("#answer")).toContainText("Source IDs:");
  await page
    .getByRole("button", { name: "Configuration studio", exact: true })
    .click();
  await page.getByLabel("Enable read-only AI").uncheck();
  await page
    .getByRole("button", { name: "Save validated configuration" })
    .click();
  await expect(page.getByRole("status")).toContainText("Configuration saved");
});

test("keyboard, accessibility, responsive overflow and scenario switching", async ({
  page,
  browserName,
}) => {
  await page.goto("/");
  await expect(page.locator(".product-card")).toHaveCount(3);
  const results = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
    .analyze();
  expect(results.violations).toEqual([]);
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
  // Windows WebKit's native link-tabbing preference differs; validate explicit focus + Enter there.
  // Chromium/Firefox/mobile also verify the first Tab stop; no app-level keyboard interception.
  if (browserName === "webkit")
    await page.getByRole("link", { name: "Skip to content" }).focus();
  else await page.keyboard.press("Tab");
  await expect(
    page.getByRole("link", { name: "Skip to content" }),
  ).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page.locator("#main")).toBeFocused();
  await page.getByLabel("Business scenario").selectOption("renewable");
  await expect(
    page.getByRole("heading", { name: "Solar panel", exact: true }),
  ).toBeVisible();
  await page.getByLabel("Business scenario").selectOption("laboratory");
  await expect(
    page.getByRole("heading", { name: "Precision balance", exact: true }),
  ).toBeVisible();
});

test("sandbox blocks source scripting and app manifest is installable", async ({
  page,
  request,
}, testInfo) => {
  await page.goto("/");
  const manifest = await request.get("/manifest.webmanifest");
  const body = await manifest.json();
  expect(body.display).toBe("standalone");
  expect((await request.get("/icon-192.png")).status()).toBe(200);
  await login(page, "employee");
  await page.getByLabel("Source file").setInputFiles({
    name: `hostile-${testInfo.project.name}.html`,
    mimeType: "text/html",
    buffer: Buffer.from(
      '<script>parent.document.body.innerHTML="pwned"</script><img src="https://attacker.test/secret"><p>Safe 2 in</p>',
    ),
  });
  await page.getByRole("button", { name: "Import & standardize" }).click();
  await expect(
    page.frameLocator("iframe").getByText("Safe 50.8 mm", { exact: true }),
  ).toBeVisible();
  await expect(page.locator("iframe")).toHaveAttribute("sandbox", "");
  expect(await page.locator(".exports a").count()).toBe(7);
  expect(await page.locator(".exports [onclick]").count()).toBe(0);
  // DOM tampering cannot turn a workspace value into markup or invalidate the existing session.
  await page.evaluate(() => {
    const select = document.querySelector<HTMLSelectElement>("#workspace")!;
    const option = document.createElement("option");
    option.value = 'industrial" onclick="alert(1)';
    select.append(option);
    select.value = option.value;
    select.dispatchEvent(new Event("change", { bubbles: true }));
  });
  await expect(page.getByRole("status")).toHaveText(
    "Unknown workspace selection.",
  );
  await expect(page.getByRole("button", { name: "Sign out" })).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Your knowledge, connected." }),
  ).toBeVisible();
  if (testInfo.project.name === "chromium") {
    await page.evaluate(() => navigator.serviceWorker.ready);
    await page.waitForFunction(
      () => navigator.serviceWorker.controller !== null,
    );
    const cached = await page.evaluate(async () => {
      const names = await caches.keys();
      return (
        await Promise.all(
          names.map(async (name) =>
            (await (await caches.open(name)).keys()).map((item) => item.url),
          ),
        )
      ).flat();
    });
    expect(
      cached.every((url) => !new URL(url).pathname.startsWith("/api/")),
    ).toBe(true);
    await page.context().setOffline(true);
    await page.goto("/");
    await expect(
      page.getByRole("heading", { name: "Your workspace needs a connection." }),
    ).toBeVisible();
  }
});
