import { downloadOpportunities } from "src/services/fetch/fetchers/searchFetcher";
import { convertSearchParamsToProperTypes } from "src/utils/search/convertSearchParamsToProperTypes";

import { NextRequest, NextResponse } from "next/server";

export const revalidate = 0;

/*
  the data flow here goes like:

  ExportSearchResultsButton click ->
  /export route ->
  downloadOpportunities ->
  fetchOpportunitySearch ->
  ExportSearchResultsButton (handle response by blobbing it to the location) -> user's file system

*/

export async function GET(request: NextRequest) {
  try {
    const searchParams = convertSearchParamsToProperTypes(
      Object.fromEntries(request.nextUrl.searchParams.entries().toArray()),
    );
    const apiResponseBody = await downloadOpportunities(searchParams);
    return new NextResponse(apiResponseBody, {
      headers: {
        "Content-Type": "text/csv",
        "Content-Disposition":
          "attachment; filename=simpler-grants-search-results.csv",
      },
    });
  } catch (e) {
    console.error("Error downloading search results", e);
    throw e;
  }
}
