import "server-only";

import { fetchOpportunitySearch } from "src/services/fetch/fetchers/fetchers";
import {
  PaginationOrderBy,
  PaginationRequestBody,
  QueryParamData,
  SearchFetcherActionType,
  SearchFilterRequestBody,
  SearchRequestBody,
} from "src/types/search/searchRequestTypes";
import { SearchAPIResponse } from "src/types/search/searchResponseTypes";

const orderByFieldLookup = {
  relevancy: "relevancy",
  opportunityNumber: "opportunity_number",
  opportunityTitle: "opportunity_title",
  agency: "agency_code",
  postedDate: "post_date",
  closeDate: "close_date",
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
  });

  const responseBody = (await response.json()) as SearchAPIResponse;

  responseBody.actionType = searchInputs.actionType;
  responseBody.fieldChanged = searchInputs.fieldChanged;

  if (!responseBody.data) {
    throw new Error("No data returned from Opportunity Search API");
  }
  return responseBody;
};

// this is very similar to `searchForOpportunities`, but
// * hardcodes some pagination params
// * sets format param = 'csv'
// * response body on success is not json, so does not parse it
export const downloadOpportunities = async (
  searchInputs: QueryParamData,
): Promise<ReadableStream<Uint8Array<ArrayBufferLike>>> => {
  const { query } = searchInputs;
  const filters = buildFilters(searchInputs);
  const pagination = buildPagination(searchInputs);

  const requestBody: SearchRequestBody = {
    pagination: { ...pagination, page_size: 5000, page_offset: 1 },
  };

  if (Object.keys(filters).length > 0) {
    requestBody.filters = filters;
  }

  if (query) {
    requestBody.query = query;
  }

  const response = await fetchOpportunitySearch({
    body: { ...requestBody, format: "csv" },
  });

  if (!response.body) {
    throw new Error("No data returned from Opportunity Search API export");
  }

  return response.body;
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

  let order_by: PaginationOrderBy = "relevancy";
  if (sortby) {
    for (const [key, value] of Object.entries(orderByFieldLookup)) {
      if (sortby.startsWith(key)) {
        order_by = value as PaginationOrderBy;
        break; // Stop searching after the first match is found
      }
    }
  }

  // sort relevancy descending without suffix
  const sort_direction =
    sortby && sortby.endsWith("Asc") ? "ascending" : "descending";

  return {
    order_by,
    page_offset,
    page_size: 25,
    sort_direction,
  };
};
