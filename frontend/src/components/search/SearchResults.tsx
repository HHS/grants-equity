import { searchForOpportunities } from "src/services/fetch/fetchers/searchFetcher";
import { QueryParamData } from "src/types/search/searchRequestTypes";

import { Suspense } from "react";

import Loading from "src/components/Loading";
import SearchPagination from "src/components/search/SearchPagination";
import SearchPaginationFetch from "src/components/search/SearchPaginationFetch";
import SearchResultsHeader from "src/components/search/SearchResultsHeader";
import SearchResultsHeaderFetch from "src/components/search/SearchResultsHeaderFetch";
import SearchResultsListFetch from "src/components/search/SearchResultsListFetch";
import { ExportSearchResultsButton } from "./ExportSearchResultsButton";

export default function SearchResults({
  searchParams,
  query,
  loadingMessage,
}: {
  searchParams: QueryParamData;
  query?: string | null;
  loadingMessage: string;
}) {
  const { page, sortby } = searchParams;

  const searchResultsPromise = searchForOpportunities(searchParams);

  const key = Object.entries(searchParams).join(",");
  const pager1key = Object.entries(searchParams).join("-") + "pager1";
  const pager2key = Object.entries(searchParams).join("-") + "pager2";
  return (
    <>
      <Suspense key={key} fallback={<SearchResultsHeader sortby={sortby} />}>
        <SearchResultsHeaderFetch
          sortby={sortby}
          queryTerm={query}
          searchResultsPromise={searchResultsPromise}
        />
      </Suspense>
      <div className="usa-prose">
        <div className="tablet-lg:display-flex">
          <ExportSearchResultsButton />
          <Suspense
            key={pager1key}
            fallback={
              <SearchPagination loading={true} page={page} query={query} />
            }
          >
            <SearchPaginationFetch
              page={page}
              query={query}
              searchResultsPromise={searchResultsPromise}
            />
          </Suspense>
        </div>
        <Suspense key={key} fallback={<Loading message={loadingMessage} />}>
          <SearchResultsListFetch searchResultsPromise={searchResultsPromise} />
        </Suspense>
        <Suspense
          key={pager2key}
          fallback={
            <SearchPagination loading={true} page={page} query={query} />
          }
        >
          <SearchPaginationFetch
            page={page}
            query={query}
            searchResultsPromise={searchResultsPromise}
            scroll={true}
          />
        </Suspense>
      </div>
    </>
  );
}
