import "server-only";

import { fetchOpportunitySearch } from "src/services/fetch/fetchers/fetchers";
import {
  PaginationOrderBy,
  PaginationRequestBody,
  PaginationSortOrder,
  QueryParamData,
  SearchFetcherActionType,
  SearchFilterRequestBody,
  SearchRequestBody,
} from "src/types/search/searchRequestTypes";

const orderByFieldLookup = {
  relevancy: ["relevancy"],
  opportunityNumber: ["opportunity_number"],
  opportunityTitle: ["opportunity_title"],
  agency: ["top_level_agency_name", "agency_name"],
  postedDate: ["post_date"],
  closeDate: ["close_date"],
};

type FrontendFilterNames =
  | "status"
  | "fundingInstrument"
  | "eligibility"
  | "agency"
  | "category";

const filterNameMap = {
  status: "opportunity_status",
  fundingInstrument: "funding_instrument",
  eligibility: "applicant_type",
  agency: "agency",
  category: "funding_category",
} as const;

export const searchForOpportunities = async (searchInputs: QueryParamData) => {
  const { query } = searchInputs;
  const filters = buildFilters(searchInputs);
  const pagination = buildPagination(searchInputs);

  const requestBody: SearchRequestBody = { pagination };

  // Only add filters if there are some
  if (Object.keys(filters).length > 0) {
    requestBody.filters = filters;
  }

  if (query) {
    requestBody.query = query;
  }

  const response = await fetchOpportunitySearch({
    body: requestBody,
    queryParamData: searchInputs,
  });

  response.actionType = searchInputs.actionType;
  response.fieldChanged = searchInputs.fieldChanged;

  if (!response.data) {
    throw new Error("No data returned from Opportunity Search API");
  }
  return response;
};

// Translate frontend filter param names to expected backend parameter names, and use one_of syntax
export const buildFilters = (
  searchInputs: QueryParamData,
): SearchFilterRequestBody => {
  return Object.entries(filterNameMap).reduce(
    (filters, [frontendFilterName, backendFilterName]) => {
      const filterData =
        searchInputs[frontendFilterName as FrontendFilterNames];
      if (filterData && filterData.size) {
        filters[backendFilterName] = { one_of: Array.from(filterData) };
      }
      return filters;
    },
    {} as SearchFilterRequestBody,
  );
};

export const buildPagination = (
  searchInputs: QueryParamData,
): PaginationRequestBody => {
  const { sortby, page, fieldChanged } = searchInputs;

  // When performing an update (query, filter, sortby change) - we want to
  // start back at the 1st page (we never want to retain the current page).
  // In addition to this statement - on the client (handleSubmit in useSearchFormState), we
  // clear the page query param and set the page back to 1.
  // On initial load (SearchFetcherActionType.InitialLoad) we honor the page the user sent. There is validation guards
  // in convertSearchParamstoProperTypes keep 1<= page <= max_possible_page
  const page_offset =
    searchInputs.actionType === SearchFetcherActionType.Update &&
    fieldChanged !== "pagination"
      ? 1
      : page;

  let sort_order: PaginationSortOrder = [
    { order_by: "relevancy", sort_direction: "descending" },
    { order_by: "post_date", sort_direction: "descending" },
  ];

  if (sortby) {
    sort_order = [];
    // this will need to change in a future where we allow the user to set an ordered set of sort columns.
    // for now we're just using the multiple internally behind a single column picker drop down so this is fine.
    for (const [key, value] of Object.entries(orderByFieldLookup)) {
      if (sortby.startsWith(key)) {
        const sort_direction =
          sortby && sortby.endsWith("Asc") ? "ascending" : "descending";
        value.forEach((item) => {
          sort_order.push({
            order_by: <PaginationOrderBy>item,
            sort_direction,
          });
          if (item === "relevancy") {
            sort_order.push({
              order_by: "post_date",
              sort_direction,
            });
          }
        });
      }
    }
  }

  return {
    page_offset,
    page_size: 25,
    sort_order,
  };
};
