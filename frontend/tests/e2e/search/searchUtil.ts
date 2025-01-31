// =========================
// Test Helper Functions
// =========================

import { expect, Locator, Page } from "@playwright/test";

export function getSearchInput(page: Page) {
  return page.locator("#query");
}

export async function fillSearchInputAndSubmit(term: string, page: Page) {
  const searchInput = getSearchInput(page);
  await searchInput.fill(term);
  await page.click(".usa-search >> button[type='submit']");
  expectURLContainsQueryParamValue(page, "query", term);
}

export function expectURLContainsQueryParamValue(
  page: Page,
  queryParamName: string,
  queryParamValue: string,
) {
  const currentURL = page.url();
  expect(currentURL).toContain(`${queryParamName}=${queryParamValue}`);
}

export async function waitForURLContainsQueryParamValue(
  page: Page,
  queryParamName: string,
  queryParamValue: string,
  timeout = 30000, // query params get set after a debounce period
) {
  const endTime = Date.now() + timeout;

  while (Date.now() < endTime) {
    const url = new URL(page.url());
    const params = new URLSearchParams(url.search);
    const actualValue = params.get(queryParamName);

    if (actualValue === queryParamValue) {
      return;
    }

    await page.waitForTimeout(500);
  }

  throw new Error(
    `URL did not contain query parameter ${queryParamName}=${queryParamValue} within ${timeout}ms`,
  );
}

export async function clickSearchNavLink(page: Page) {
  await page.click("nav >> text=Search");
}

export function getMobileMenuButton(page: Page) {
  return page.locator("button >> text=MENU");
}

export async function hasMobileMenu(page: Page) {
  const menuButton = getMobileMenuButton(page);
  return await menuButton.isVisible();
}

export async function clickMobileNavMenu(menuButton: Locator) {
  await menuButton.click();
}

export async function expectCheckboxIDIsChecked(
  page: Page,
  idWithHash: string,
) {
  const checkbox: Locator = page.locator(idWithHash);
  await expect(checkbox).toBeChecked();
}

export async function toggleCheckboxes(
  page: Page,
  checkboxObject: Record<string, string>,
  queryParamName: string,
) {
  let runningQueryParams = "";
  for (const [checkboxID, queryParamValue] of Object.entries(checkboxObject)) {
    await toggleCheckbox(page, checkboxID);
    runningQueryParams += runningQueryParams
      ? `,${queryParamValue}`
      : queryParamValue;
    await waitForURLContainsQueryParamValue(
      page,
      queryParamName,
      runningQueryParams,
    );
  }
}

export async function toggleCheckbox(page: Page, idWithoutHash: string) {
  const checkBox = page.locator(`label[for=${idWithoutHash}]`);
  await checkBox.isEnabled();
  await checkBox.click();
}

export async function refreshPageWithCurrentURL(page: Page) {
  const currentURL = page.url();
  await page.goto(currentURL); // go to new url in same tab
  return page;
}

export async function selectSortBy(page: Page, sortByValue: string) {
  await page.locator("#search-sort-by-select").selectOption(sortByValue);
}

export async function waitForSearchResultsLoaded(page: Page) {
  // Wait for number of opportunities to show
  const resultsHeading = page.locator('h2:has-text("Opportunities")');
  await resultsHeading.waitFor({ state: "visible", timeout: 60000 });
}

export async function clickAccordionWithTitle(
  page: Page,
  accordionTitle: string,
) {
  await page
    .locator(`button.usa-accordion__button:has-text("${accordionTitle}")`)
    .click();
}
