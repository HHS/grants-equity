"use server";

import { SearchAPIResponse } from "src/types/search/searchResponseTypes";

import SearchPagination from "src/components/search/SearchPagination";

interface SearchPaginationProps {
  searchResultsPromise: Promise<SearchAPIResponse>;
  // Determines whether clicking on pager items causes a scroll to the top of the search
  // results. Created so the bottom pager can scroll.
  scroll?: boolean;
  page: number;
  query?: string | null;
}

export default async function SearchPaginationFetch({
  page,
  query,
  searchResultsPromise,
  scroll = false,
}: SearchPaginationProps) {
  const searchResults = await searchResultsPromise;
  const totalPages = searchResults.pagination_info?.total_pages;
  const totalResults = searchResults.pagination_info?.total_records;

  return (
    <>
      <SearchPagination
        totalPages={totalPages}
        page={page}
        query={query}
        scroll={scroll}
        totalResults={String(totalResults)}
      />
    </>
  );
}
