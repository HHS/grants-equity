import { axe } from "jest-axe";
import { render, screen } from "tests/react-utils";

import { ExportSearchResultsButton } from "src/components/search/ExportSearchResultsButton";

const mockDownloadSearchResultsCSV = jest.fn();

const fakeSearchParams = new URLSearchParams();

jest.mock(
  "src/services/fetch/fetchers/clientSearchResultsDownloadFetcher",
  () => ({
    downloadSearchResultsCSV: (params: unknown): unknown =>
      Promise.resolve(mockDownloadSearchResultsCSV(params)),
  }),
);

jest.mock("next/navigation", () => ({
  useSearchParams: () => fakeSearchParams,
}));

describe("ExportSearchResultsButton", () => {
  afterEach(() => {
    jest.resetAllMocks();
  });
  it("should not have basic accessibility issues", async () => {
    const { container } = render(<ExportSearchResultsButton />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it("calls downloadSearchResultsCSV with correct args on button click", () => {
    render(<ExportSearchResultsButton />);
    const button = screen.getByRole("button");
    button.click();

    expect(mockDownloadSearchResultsCSV).toHaveBeenCalledWith(fakeSearchParams);
  });
});
