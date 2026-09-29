import { test, expect } from "@playwright/test";

test("demo investigation, evidence, report and persisted case", async ({
  page,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto("/");
  await page
    .getByRole("button", { name: "Explore demo investigation" })
    .click();
  await expect(page.getByText("Why Binance (demo)?")).toBeVisible();
  await expect(page.getByText("$18,000", { exact: true })).toBeVisible();
  await expect(page.locator(".react-flow__node").first()).toBeVisible();
  await page.screenshot({
    path: "test-results/dashboard-desktop.png",
    fullPage: true,
  });
  await page.getByRole("button", { name: /02 Coinbase/ }).click();
  await expect(page.getByText("Why Coinbase (demo)?")).toBeVisible();
  await page.getByLabel("Graph hop depth").selectOption("2");
  await expect(page.locator(".react-flow__node")).toHaveCount(10);
  await page.getByRole("button", { name: "Transactions", exact: true }).click();
  await page.locator("tbody tr").first().click();
  await expect(
    page.getByRole("dialog", { name: "Evidence details" }),
  ).toBeVisible();
  await expect(
    page.getByText("transaction detail", { exact: false }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Close evidence" }).click();
  await page.getByRole("button", { name: "Report", exact: true }).click();
  await expect(page.locator(".report pre")).toContainText(
    "Evidence digest (SHA-256)",
  );
  const download = page.waitForEvent("download");
  await page.getByRole("button", { name: "Export report" }).click();
  expect((await download).suggestedFilename()).toMatch(/CASE-.*\.md/);
  await page.reload();
  await page.getByRole("button", { name: "Case library", exact: true }).click();
  await page.locator(".case-list-item").first().click();
  await expect(page.getByText("Why Binance (demo)?")).toBeVisible();
  expect(errors).toEqual([]);
});

test("imported empty case produces no fabricated candidate", async ({
  page,
}) => {
  await page.goto("/");
  await page
    .locator("input[type=file]")
    .setInputFiles({
      name: "empty.json",
      mimeType: "application/json",
      buffer: Buffer.from(
        JSON.stringify({
          target: "0x0000000000000000000000000000000000000001",
          chain: "ethereum",
          mode: "import",
          transactions: [],
          labels: [],
        }),
      ),
    });
  await expect(
    page.getByText("No VASP endpoint is supported by this evidence."),
  ).toBeVisible();
  await expect(
    page.getByText("Imported evidence", { exact: true }),
  ).toBeVisible();
});

test("mobile dashboard remains navigable", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await page
    .getByRole("button", { name: "Explore demo investigation" })
    .click();
  await expect(page.getByText("Why Binance (demo)?")).toBeVisible();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
  await page.screenshot({
    path: "test-results/dashboard-mobile.png",
    fullPage: true,
  });
});
