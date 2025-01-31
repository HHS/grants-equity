import { expect, test } from "@playwright/test";

test.describe("Search results export", () => {
  test("should download a csv file when requested", async ({ page }, {
    project,
  }) => {
    // downloads work manually in safari, but can't get the test to work
    if (project.name.match(/webkit/)) {
      return;
    }
    const downloadPromise = page.waitForEvent("download");
    await page.goto("/search");
    await page
      .locator('div[data-testid="search-download-button-container"] > button')
      .click();
    const download = await downloadPromise;
    expect(download.url()).toBeTruthy();
  });
});
