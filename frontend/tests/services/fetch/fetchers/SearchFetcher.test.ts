import {
  buildFilters,
  buildPagination,
  searchForOpportunities,
} from "src/services/fetch/fetchers/searchFetcher";
import {
  QueryParamData,
  SearchFetcherActionType,
} from "src/types/search/searchRequestTypes";
import { SearchAPIResponse } from "src/types/search/searchResponseTypes";

const searchProps: QueryParamData = {
  page: 1,
  status: new Set(["forecasted", "posted"]),
  fundingInstrument: new Set(["grant", "cooperative_agreement"]),
  agency: new Set(),
  category: new Set(),
  eligibility: new Set(),
  query: "research",
  sortby: "opportunityNumberAsc",
  actionType: "fun" as SearchFetcherActionType,
  fieldChanged: "baseball",
};

const mockfetchOpportunitySearch = jest.fn().mockResolvedValue({ data: {} });

jest.mock("react", () => ({
  ...jest.requireActual<typeof import("react")>("react"),
  cache: (fn: unknown) => fn,
}));

jest.mock("src/services/fetch/fetchers/fetchers", () => ({
  fetchOpportunitySearch: (params: QueryParamData) => {
    return mockfetchOpportunitySearch(params) as SearchAPIResponse;
  },
}));

describe("searchForOpportunities", () => {
  it("calls request function with correct parameters", async () => {
    const result = await searchForOpportunities(searchProps);

    expect(mockfetchOpportunitySearch).toHaveBeenCalledWith({
      body: {
        pagination: {
          sort_order: [
            {
              order_by: "opportunity_number",
              sort_direction: "ascending",
            },
          ], // This should be the actual value being used in the API method
          page_offset: 1,
          page_size: 25,
        },
        query: "research",
        filters: {
          opportunity_status: {
            one_of: ["forecasted", "posted"],
          },
          funding_instrument: {
            one_of: ["grant", "cooperative_agreement"],
          },
        },
      },
      queryParamData: {
        actionType: "fun",
        agency: new Set(),
        category: new Set(),
        eligibility: new Set(),
        fieldChanged: "baseball",
        fundingInstrument: new Set(["grant", "cooperative_agreement"]),
        page: 1,
        query: "research",
        sortby: "opportunityNumberAsc",
        status: new Set(["forecasted", "posted"]),
      },
    });

    expect(result).toEqual({
      actionType: "fun",
      data: {},
      fieldChanged: "baseball",
    });
  });
});

describe("buildFilters", () => {
  it("maps all params to the correct filter names", () => {
    const filters = buildFilters({
      ...searchProps,
      ...{
        agency: new Set(["agency 1", "agency 2"]),
        category: new Set(["category 1", "category 2"]),
        eligibility: new Set(["applicant type 1", "applicant type 2"]),
      },
    });
    expect(filters.opportunity_status).toEqual({
      one_of: ["forecasted", "posted"],
    });
    expect(filters.funding_instrument).toEqual({
      one_of: ["grant", "cooperative_agreement"],
    });
    expect(filters.applicant_type).toEqual({
      one_of: ["applicant type 1", "applicant type 2"],
    });
    expect(filters.agency).toEqual({
      one_of: ["agency 1", "agency 2"],
    });
    expect(filters.funding_category).toEqual({
      one_of: ["category 1", "category 2"],
    });
  });
  it("does not add filters where params are absent", () => {
    const filters = buildFilters(searchProps);
    expect(filters.opportunity_status).toEqual({
      one_of: ["forecasted", "posted"],
    });
    expect(filters.funding_instrument).toEqual({
      one_of: ["grant", "cooperative_agreement"],
    });
    expect(filters.applicant_type).toEqual(undefined);
    expect(filters.agency).toEqual(undefined);
    expect(filters.funding_category).toEqual(undefined);
  });
});

describe("buildPagination", () => {
  it("builds correct pagination with defaults", () => {
    const pagination = buildPagination({
      ...searchProps,
      ...{ page: 5, sortby: null },
    });

    expect(pagination.sort_order[0].order_by).toEqual("relevancy");
    expect(pagination.page_offset).toEqual(5);
    expect(pagination.sort_order[0].sort_direction).toEqual("descending");
  });

  it("builds correct offset based on action type and field changed", () => {
    const pagination = buildPagination({
      ...searchProps,
      ...{ page: 5, actionType: SearchFetcherActionType.Update },
    });

    expect(pagination.page_offset).toEqual(1);

    const secondPagination = buildPagination({
      ...searchProps,
      ...{ page: 5, actionType: SearchFetcherActionType.InitialLoad },
    });

    expect(secondPagination.page_offset).toEqual(5);

    const thirdPagination = buildPagination({
      ...searchProps,
      ...{
        page: 5,
        actionType: SearchFetcherActionType.Update,
        fieldChanged: "pagination",
      },
    });

    expect(thirdPagination.page_offset).toEqual(5);

    const fourthPagination = buildPagination({
      ...searchProps,
      ...{
        page: 5,
        actionType: SearchFetcherActionType.Update,
        fieldChanged: "not_pagination",
      },
    });

    expect(fourthPagination.page_offset).toEqual(1);
  });

  it("builds correct order_by based on sortby", () => {
    const pagination = buildPagination({
      ...searchProps,
      ...{ sortby: "closeDateAsc" },
    });

    expect(pagination.sort_order[0].order_by).toEqual("close_date");

    const secondPagination = buildPagination({
      ...searchProps,
      ...{ sortby: "postedDateAsc" },
    });

    expect(secondPagination.sort_order[0].order_by).toEqual("post_date");
  });

  it("builds correct sort_direction based on sortby", () => {
    const pagination = buildPagination({
      ...searchProps,
      ...{ sortby: "opportunityNumberDesc" },
    });

    expect(pagination.sort_order[0].sort_direction).toEqual("descending");

    const secondPagination = buildPagination({
      ...searchProps,
      ...{ sortby: "postedDateAsc" },
    });

    expect(secondPagination.sort_order[0].sort_direction).toEqual("ascending");

    const thirdPagination = buildPagination({
      ...searchProps,
      ...{ sortby: null },
    });

    expect(thirdPagination.sort_order[0].sort_direction).toEqual("descending");
  });
});
