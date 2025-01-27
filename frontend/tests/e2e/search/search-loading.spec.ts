import skip, { expect, test } from "@playwright/test";
import { chromium } from "playwright-core";
import {
  fillSearchInputAndSubmit,
  generateRandomString,
} from "tests/e2e/search/searchSpecUtil";

test.describe("Search page tests", () => {
  // Loadiing indicator resolves too quickly to reliably test in e2e.
  skip("should show and hide loading state", async () => {
    const searchTerm = generateRandomString([4, 5]);
    const searchTerm2 = generateRandomString([8]);

    const browser = await chromium.launch({ slowMo: 100 });

    const page = await browser.newPage();
    await page.goto("/search");
    const loadingIndicator = page.locator(
      'span[data-testid="loading-message"]',
    );

    await fillSearchInputAndSubmit(searchTerm, page);
    await expect(loadingIndicator).toBeVisible();
    await expect(loadingIndicator).toBeHidden();

    await fillSearchInputAndSubmit(searchTerm2, page);
    await expect(loadingIndicator).toBeVisible();
    await expect(loadingIndicator).toBeHidden();
  });
});
