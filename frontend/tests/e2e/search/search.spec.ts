import { expect, test } from "@playwright/test";
import { camelCase } from "lodash";
import { PageProps } from "tests/e2e/playwrightUtils";
import {
  clickAccordionWithTitle,
  clickLastPaginationPage,
  clickPaginationPageNumber,
  expectCheckboxIDIsChecked,
  expectSortBy,
  fillSearchInputAndSubmit,
  getFirstSearchResultTitle,
  getLastSearchResultTitle,
  getNumberOfOpportunitySearchResults,
  getSearchInput,
  refreshPageWithCurrentURL,
  selectAllTopLevelFilterOptions,
  selectSortBy,
  toggleCheckboxes,
  toggleMobileSearchFilters,
  validateTopLevelAndNestedSelectedFilterCounts,
  waitForAnyURLChange,
  waitForSearchResultsInitialLoad,
  waitForUrl,
  waitForURLContainsQueryParam,
} from "tests/e2e/search/searchSpecUtil";

test.describe("Search page tests", () => {
  test("should refresh and retain filters in a new tab", async ({ page }, {
    project,
  }) => {
    await page.goto("/search");

    // Set all inputs, then refresh the page. Those same inputs should be
    // set from query params.
    const searchTerm = "education";
    const statusCheckboxes = {
      "status-closed": "closed",
    };
    const fundingInstrumentCheckboxes = {
      "funding-instrument-cooperative_agreement": "cooperative_agreement",
      "funding-instrument-grant": "grant",
    };

    const eligibilityCheckboxes = {
      "eligibility-state_governments": "state_governments",
      "eligibility-county_governments": "county_governments",
    };
    const agencyCheckboxes = {
      EPA: "EPA",
      AC: "AC",
    };
    const categoryCheckboxes = {
      "category-recovery_act": "recovery_act",
      "category-agriculture": "agriculture",
    };

    await waitForSearchResultsInitialLoad(page);

    await selectSortBy(page, "agencyDesc");

    if (project.name.match(/[Mm]obile/)) {
      await toggleMobileSearchFilters(page);
    }

    await fillSearchInputAndSubmit(searchTerm, page);

    await toggleCheckboxes(
      page,
      statusCheckboxes,
      "status",
      "forecasted,posted",
    );

    await clickAccordionWithTitle(page, "Funding instrument");
    await toggleCheckboxes(
      page,
      fundingInstrumentCheckboxes,
      "fundingInstrument",
    );

    await clickAccordionWithTitle(page, "Eligibility");
    await toggleCheckboxes(page, eligibilityCheckboxes, "eligibility");

    await clickAccordionWithTitle(page, "Agency");
    await toggleCheckboxes(page, agencyCheckboxes, "agency");

    await clickAccordionWithTitle(page, "Category");
    await toggleCheckboxes(page, categoryCheckboxes, "category");

    /***********************************************************/
    /* Page refreshed should have all the same inputs selected
    /***********************************************************/

    await refreshPageWithCurrentURL(page);

    // Expect search inputs are retained in the new tab
    await expectSortBy(page, "agencyDesc");
    const searchInput = getSearchInput(page);
    await expect(searchInput).toHaveValue(searchTerm);

    for (const [checkboxID] of Object.entries(statusCheckboxes)) {
      await expectCheckboxIDIsChecked(page, `#${checkboxID}`);
    }

    for (const [checkboxID] of Object.entries(fundingInstrumentCheckboxes)) {
      await expectCheckboxIDIsChecked(page, `#${checkboxID}`);
    }
    for (const [checkboxID] of Object.entries(eligibilityCheckboxes)) {
      await expectCheckboxIDIsChecked(page, `#${checkboxID}`);
    }
    for (const [checkboxID] of Object.entries(agencyCheckboxes)) {
      await expectCheckboxIDIsChecked(page, `#${checkboxID}`);
    }
    for (const [checkboxID] of Object.entries(categoryCheckboxes)) {
      await expectCheckboxIDIsChecked(page, `#${checkboxID}`);
    }
  });

  test("resets page back to 1 when choosing a filter", async ({ page }, {
    project,
  }) => {
    await page.goto("/search?status=none");
    await clickPaginationPageNumber(page, 2);

    // Verify that page 1 is highlighted
    let currentPageButton = page
      .locator(".usa-pagination__button.usa-current")
      .first();
    await expect(currentPageButton).toHaveAttribute("aria-label", "Page 2");

    // Select the 'Closed' checkbox under 'Opportunity status'
    const statusCheckboxes = {
      "status-closed": "closed",
    };

    if (project.name.match(/[Mm]obile/)) {
      await toggleMobileSearchFilters(page);
    }

    await toggleCheckboxes(page, statusCheckboxes, "status");

    // Wait for the page to reload
    await waitForSearchResultsInitialLoad(page);

    // Verify that page 1 is highlighted
    currentPageButton = page
      .locator(".usa-pagination__button.usa-current")
      .first();
    await expect(currentPageButton).toHaveAttribute("aria-label", "Page 1");

    // It should not have a page query param set
    await page.waitForURL("search?status=closed");
  });

  test("last result becomes first result when flipping sort order", async ({
    page,
  }: PageProps) => {
    await page.goto("/search");
    await waitForSearchResultsInitialLoad(page);

    await selectSortBy(page, "opportunityTitleDesc");

    await clickLastPaginationPage(page);

    const lastSearchResultTitle = await getLastSearchResultTitle(page);

    await selectSortBy(page, "opportunityTitleAsc");

    const firstSearchResultTitle = await getFirstSearchResultTitle(page);

    expect(firstSearchResultTitle).toBe(lastSearchResultTitle);
  });

  test("number of results is the same with none or all opportunity status checked", async ({
    page,
  }, { project }) => {
    await page.goto("/search?status=none");
    const initialSearchResultsCount =
      await getNumberOfOpportunitySearchResults(page);

    // check all 4 boxes
    const statusCheckboxes = {
      "status-forecasted": "forecasted",
      "status-posted": "posted",
      "status-closed": "closed",
      "status-archived": "archived",
    };

    if (project.name.match(/[Mm]obile/)) {
      await toggleMobileSearchFilters(page);
    }

    await toggleCheckboxes(page, statusCheckboxes, "status");

    const updatedSearchResultsCount =
      await getNumberOfOpportunitySearchResults(page);

    expect(initialSearchResultsCount).toBe(updatedSearchResultsCount);
  });
  test.describe("selecting and clearing filters", () => {
    const filterTypes = [
      "Funding instrument",
      "Eligibility",
      "Category",
      "Agency",
    ];

    filterTypes.forEach((filterType) => {
      test(`correctly clears and selects all for ${filterType} filters`, async ({
        page,
      }, { project }) => {
        const camelCaseFilterType = camelCase(filterType);
        // load search page
        await page.goto("/search");

        const initialSearchResultsCount =
          await getNumberOfOpportunitySearchResults(page);

        // open accordion for filter type
        if (project.name.match(/[Mm]obile/)) {
          await toggleMobileSearchFilters(page);
        }

        await clickAccordionWithTitle(page, filterType);

        const numberOfFilterOptions = await selectAllTopLevelFilterOptions(
          page,
          camelCaseFilterType,
        );

        // validate that new search results are returned
        let updatedSearchResultsCount =
          await getNumberOfOpportunitySearchResults(page);
        expect(initialSearchResultsCount).not.toBe(updatedSearchResultsCount);

        // validate that checkboxes are checked
        let checkboxes = await page
          .locator(
            `#opportunity-filter-${camelCaseFilterType} > ul > li > div > input`,
          )
          .all();

        await Promise.all(
          checkboxes.map((checkbox) => expect(checkbox).toBeChecked()),
        );

        // validate that the correct number of filter options is displayed
        const accordionButton = page.locator(
          `button[data-testid="accordionButton_opportunity-filter-${camelCaseFilterType}"]`,
        );

        await expect(accordionButton).toHaveText(
          `${filterType}${numberOfFilterOptions}`,
        );

        // click clear all
        await page
          .locator(
            `#opportunity-filter-${camelCaseFilterType} button:has-text("Clear All")`,
          )
          .first()
          .click();

        // validate that url is updated
        await waitForUrl(page, "http://127.0.0.1:3000/search");

        // validate that new search results are returned
        updatedSearchResultsCount =
          await getNumberOfOpportunitySearchResults(page);
        expect(initialSearchResultsCount).toBe(updatedSearchResultsCount);

        // validate that checkboxes are not checked
        checkboxes = await page
          .locator(
            `#opportunity-filter-${camelCaseFilterType} > ul > li > div > input`,
          )
          .all();

        await Promise.all(
          checkboxes.map((checkbox) => expect(checkbox).not.toBeChecked()),
        );

        // validate that the correct number of filter options is displayed
        await expect(accordionButton).toHaveText(filterType);
      });
    });

    /*
      Scenarios

      - click select all agencies -> click select all nested agency
      - click clear all
      - click select all nested agency -> click select all agencies
      - click clear all nested agency
    */
    test("selects and clears nested agency filters", async ({ page }, {
      project,
    }) => {
      const nestedFilterCheckboxesSelector =
        "#opportunity-filter-agency > ul > li:first-child > div > div input";

      await page.goto("/search");

      const initialSearchResultsCount =
        await getNumberOfOpportunitySearchResults(page);

      // open accordion for filter type
      if (project.name.match(/[Mm]obile/)) {
        await toggleMobileSearchFilters(page);
      }

      await clickAccordionWithTitle(page, "Agency");

      // gather number of (top level) filter options
      // and select all top level filter options
      const numberOfTopLevelFilterOptions =
        await selectAllTopLevelFilterOptions(page, "agency");

      const topLevelSelectedNumberOfSearchResults =
        await getNumberOfOpportunitySearchResults(page);

      // open first nested agency and get number of nested options
      const firstExpander = page
        .locator('#opportunity-filter-agency svg[aria-label="Expand section"]')
        .first();
      await firstExpander.click();

      const numberOfNestedFilterOptions = await page
        .locator(nestedFilterCheckboxesSelector)
        .count();

      let urlBeforeInteraction = page.url();

      // click nested select all for first nested agency in list
      const selectAllNestedButton = page
        .locator('#opportunity-filter-agency button:has-text("Select All")')
        .nth(1);
      await selectAllNestedButton.click();

      await waitForAnyURLChange(page, urlBeforeInteraction);

      // validate that new search results are returned with filtered (smaller number) of results
      const topLevelAndNestedSelectedNumberOfSearchResults =
        await getNumberOfOpportunitySearchResults(page);

      expect(
        topLevelAndNestedSelectedNumberOfSearchResults,
      ).toBeLessThanOrEqual(topLevelSelectedNumberOfSearchResults);

      // validate that nested checkboxes are checked
      let checkboxes = await page.locator(nestedFilterCheckboxesSelector).all();

      await Promise.all(
        checkboxes.map((checkbox) => expect(checkbox).toBeChecked()),
      );

      // validate that the correct number of filter options is displayed
      const accordionButton = page.locator(
        'button[data-testid="accordionButton_opportunity-filter-agency"]',
      );

      await expect(accordionButton).toHaveText(
        `Agency${numberOfTopLevelFilterOptions + numberOfNestedFilterOptions}`,
      );

      const expanderButton = page.locator(
        "#opportunity-filter-agency > ul > li:first-child > div > button",
      );

      await expect(expanderButton).toContainText(
        `${numberOfNestedFilterOptions}`,
      );

      await validateTopLevelAndNestedSelectedFilterCounts(
        page,
        "Agency",
        numberOfTopLevelFilterOptions,
        numberOfNestedFilterOptions,
      );

      // click top level clear all
      await page
        .locator(`#opportunity-filter-agency button:has-text("Clear All")`)
        .first()
        .click();

      // validate that url is updated
      await waitForUrl(page, "http://127.0.0.1:3000/search");

      // validate that new search results are returned with no filters in place (all results)
      const fullyClearedSearchResultsCount =
        await getNumberOfOpportunitySearchResults(page);
      expect(initialSearchResultsCount).toBe(fullyClearedSearchResultsCount);

      // validate that nested checkboxes are not checked
      checkboxes = await page.locator(nestedFilterCheckboxesSelector).all();

      await Promise.all(
        checkboxes.map((checkbox) => expect(checkbox).not.toBeChecked()),
      );

      // validate that the correct number of filter options is displayed
      await expect(accordionButton).toHaveText("Agency");

      // select all from first nested agency
      await selectAllNestedButton.click();

      await waitForURLContainsQueryParam(page, "agency");

      // validate that new filtered search results are returned for nested agency, and correct counts displayed
      // (fewer results than with top level agencies + nested agencies selected)
      const nestedSelectedNumberOfSearchResults =
        await getNumberOfOpportunitySearchResults(page);

      expect(nestedSelectedNumberOfSearchResults).toBeLessThanOrEqual(
        topLevelAndNestedSelectedNumberOfSearchResults,
      );

      await validateTopLevelAndNestedSelectedFilterCounts(
        page,
        "Agency",
        0,
        numberOfNestedFilterOptions,
      );

      // select all top level agencies
      urlBeforeInteraction = page.url();
      await selectAllTopLevelFilterOptions(page, "agency");

      await waitForAnyURLChange(page, urlBeforeInteraction);

      const newTopLevelAndNestedSelectedNumberOfSearchResults =
        await getNumberOfOpportunitySearchResults(page);

      // validate that counts equal previous counts for this state (top level and first nested agency selected)
      expect(newTopLevelAndNestedSelectedNumberOfSearchResults).toEqual(
        topLevelAndNestedSelectedNumberOfSearchResults,
      );

      await validateTopLevelAndNestedSelectedFilterCounts(
        page,
        "Agency",
        numberOfTopLevelFilterOptions,
        numberOfNestedFilterOptions,
      );

      urlBeforeInteraction = page.url();

      // clear nested agency selection
      await page
        .locator(`#opportunity-filter-agency button:has-text("Clear All")`)
        .nth(1)
        .click();

      // validate that url is updated
      await waitForAnyURLChange(page, urlBeforeInteraction);

      // validate that new unfiltered filtered results are returned with fewer results than with
      // sub-agencies selected
      const partiallyClearedSearchResultsCount =
        await getNumberOfOpportunitySearchResults(page);
      expect(partiallyClearedSearchResultsCount).toBeLessThanOrEqual(
        topLevelAndNestedSelectedNumberOfSearchResults,
      );

      // validate that nested agency checkboxes are not checked
      checkboxes = await page.locator(nestedFilterCheckboxesSelector).all();

      await Promise.all(
        checkboxes.map((checkbox) => expect(checkbox).not.toBeChecked()),
      );

      // validate that the correct number of filter options is displayed
      await validateTopLevelAndNestedSelectedFilterCounts(
        page,
        "Agency",
        numberOfTopLevelFilterOptions,
        0,
      );
    });
  });
});
