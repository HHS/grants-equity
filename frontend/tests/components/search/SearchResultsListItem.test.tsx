import { axe } from "jest-axe";
import { Opportunity } from "src/types/search/searchResponseTypes";
import { render, screen, waitFor } from "tests/react-utils";

import React from "react";

import SearchResultsListItem from "src/components/search/SearchResultsListItem";

const mockOpportunity: Opportunity = {
  opportunity_id: 12345,
  opportunity_title: "Test Opportunity",
  opportunity_status: "posted",
  summary: {
    archive_date: "2023-01-01",
    close_date: "2023-02-01",
    post_date: "2023-01-15",
    agency_name: "Test Agency",
    award_ceiling: 50000,
    award_floor: 10000,
  },
  opportunity_number: "OPP-12345",
} as Opportunity;

jest.mock("src/services/globalState/GlobalStateProvider", () => ({
  useGlobalState: () => ({
    flattenedAgencyOptions: [{ id: "hi", label: "yes", value: "sure" }],
  }),
}));

describe("SearchResultsListItem", () => {
  it("should not have basic accessibility issues", async () => {
    const { container } = render(
      <SearchResultsListItem opportunity={mockOpportunity} />,
    );
    const results = await waitFor(() => axe(container));
    expect(results).toHaveNoViolations();
  });

  it("renders opportunity title and number", () => {
    render(<SearchResultsListItem opportunity={mockOpportunity} />);
    expect(screen.getByText("Test Opportunity")).toBeInTheDocument();
    expect(screen.getByText("OPP-12345")).toBeInTheDocument();
  });

  getDateTestCases().forEach(({ api_date, ui_date }) => {
    it(`renders formatted date ${ui_date} for API date ${api_date}`, () => {
      const opportunityWithDate = {
        ...mockOpportunity,
        summary: {
          ...mockOpportunity.summary,
          post_date: api_date,
        },
      };

      render(<SearchResultsListItem opportunity={opportunityWithDate} />);
      expect(screen.getByText(ui_date)).toBeInTheDocument();
    });
  });
});

function getDateTestCases() {
  return [
    { api_date: "2024-05-01", ui_date: "May 1, 2024" },
    { api_date: "2023-07-21", ui_date: "July 21, 2023" },
    { api_date: "2022-11-30", ui_date: "November 30, 2022" },
    { api_date: "2021-01-15", ui_date: "January 15, 2021" },
    { api_date: "2020-06-17", ui_date: "June 17, 2020" },
    { api_date: "2019-08-25", ui_date: "August 25, 2019" },
    { api_date: "2018-12-05", ui_date: "December 5, 2018" },
    { api_date: "2017-09-13", ui_date: "September 13, 2017" },
    { api_date: "2016-04-07", ui_date: "April 7, 2016" },
    { api_date: "2015-03-23", ui_date: "March 23, 2015" },
  ];
}
