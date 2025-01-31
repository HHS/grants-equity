import { render, screen } from "@testing-library/react";
import { identity } from "lodash";
import { useTranslationsMock } from "src/utils/testing/intlMocks";

import { Accordion } from "@trussworks/react-uswds";

import SearchFilters from "src/components/search/SearchFilters";

const mockUpdateQueryParams = jest.fn();

jest.mock("src/hooks/useSearchParamUpdater", () => ({
  useSearchParamUpdater: () => ({
    updateQueryParams: mockUpdateQueryParams,
  }),
}));

jest.mock("next-intl/server", () => ({
  getTranslations: () => identity,
  setRequestLocale: identity,
}));

jest.mock("next-intl", () => ({
  useTranslations: () => useTranslationsMock(),
}));

jest.mock("src/services/globalState/GlobalStateProvider", () => ({
  useGlobalState: () => ({
    setAgencyOptions: () => undefined,
  }),
}));

// otherwise we have to deal with mocking suspense
jest.mock(
  "src/components/search/SearchFilterAccordion/AgencyFilterAccordion",
  () => ({
    AgencyFilterAccordion: () => {
      return (
        <Accordion
          bordered={true}
          items={[
            {
              title: "agency",
              content: [],
              expanded: false,
              id: `opportunity-filter-agency-disabled`,
              headingLevel: "h2",
            },
          ]}
          multiselectable={true}
          className="margin-top-4"
        />
      );
    },
  }),
);

jest.mock("src/services/fetch/fetchers/agenciesFetcher", () => ({
  getAgenciesForFilterOptions: () =>
    Promise.resolve([
      {
        id: "NARA",
        label: "National Archives and Records Administration",
        value: "NARA",
      },
      {
        id: "NASA",
        label: "National Aeronautics and Space Administration",
        value: "NASA",
        children: [
          {
            id: "NASA-GSFC",
            label: "NASA Goddard Space Flight Center",
            value: "NASA-GSFC",
          },
          {
            id: "NASA-HQ",
            label: "NASA Headquarters",
            value: "NASA-HQ",
          },
        ],
      },
    ]),
}));

describe("SearchFilters", () => {
  it("Renders without errors", () => {
    render(
      <SearchFilters
        fundingInstrument={new Set()}
        eligibility={new Set()}
        agency={new Set()}
        category={new Set()}
        opportunityStatus={new Set()}
      />,
    );

    // making weird use of the mocked translation behavior to make sure that things render correctly, but w/e
    const component = screen.getByText("accordion.titles.funding");
    expect(component).toBeInTheDocument();
  });
});
