import { SEARCH_NO_STATUS_VALUE } from "src/constants/search";
import {
  QueryParamData,
  QuerySetParam,
  SearchFetcherActionType,
  SortOptions,
} from "src/types/search/searchRequestTypes";
import { OptionalStringDict } from "src/types/searchRequestURLTypes";

// Search params (query string) coming from the request URL into the server
// can be a string, string[], or undefined.
// Process all of them so they're just a string (or number for page)

// The above doesn't seem to still be true, should we update? - DWS
export function convertSearchParamsToProperTypes(
  params: OptionalStringDict,
): QueryParamData {
  return {
    ...params,
    query: params.query || "", // Convert empty string to null if needed
    status: paramToSet(params.status, "status"),
    fundingInstrument: paramToSet(params.fundingInstrument),
    eligibility: paramToSet(params.eligibility),
    agency: paramToSet(params.agency),
    category: paramToSet(params.category),
    sortby: (params.sortby as SortOptions) || null, // Convert empty string to null if needed

    // Ensure page is at least 1 or default to 1 if undefined
    page: getSafePage(params.page),
    actionType: SearchFetcherActionType.InitialLoad,
  };
}

// Helper function to convert query parameters to set
// and to reset that status params none if status=none is set
function paramToSet(param: QuerySetParam, type?: string): Set<string> {
  if (!param && type === "status") {
    return new Set(["forecasted", "posted"]);
  }

  if (!param || (type === "status" && param === SEARCH_NO_STATUS_VALUE)) {
    return new Set();
  }

  if (Array.isArray(param)) {
    return new Set(param);
  }
  return new Set(param.split(","));
}

// Keeps page >= 1.
// (We can't enforce a max here since this is before the API request)
function getSafePage(page: string | undefined) {
  return Math.max(1, parseInt(page || "1"));
}
