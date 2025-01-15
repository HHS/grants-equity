"use client";

import { QueryContext } from "src/app/[locale]/search/QueryProvider";
import { useSearchParamUpdater } from "src/hooks/useSearchParamUpdater";

import { useContext, useEffect } from "react";
import { Pagination } from "@trussworks/react-uswds";

export enum PaginationPosition {
  Top = "topPagination",
  Bottom = "bottomPagination",
}

interface SearchPaginationProps {
  page: number;
  query: string | null | undefined;
  totalPages?: number | null;
  scroll?: boolean;
  totalResults?: string;
  loading?: boolean;
}

const MAX_SLOTS = 7;

// in addition to handling client side page navigation, this client component handles setting client state for:
// - total pages of search results
// - total number of search results
export default function SearchPagination({
  page,
  query,
  totalPages = null,
  scroll = false,
  totalResults = "",
  loading = false,
}: SearchPaginationProps) {
  const { updateQueryParams } = useSearchParamUpdater();
  const {
    updateTotalPages,
    updateTotalResults,
    totalPages: totalPagesFromQuery,
  } = useContext(QueryContext);

  // will re-run on each fetch, as we switch from the Suspended version of the component to the live one
  useEffect(() => {
    if (!loading) {
      updateTotalPages(String(totalPages));
    }
  }, [updateTotalPages, totalPages, loading]);

  useEffect(() => {
    if (!loading) {
      updateTotalResults(String(totalResults));
    }
  }, [updateTotalResults, totalResults, loading]);

  const updatePage = (page: number) => {
    updateQueryParams(String(page), "page", query, scroll);
  };

  // Shows total pages from the query context before it is re-fetched from the API.
  // This is only used for display due to race conditions, otherwise totalPages prop
  // is the source of truth
  const pageCount = totalPages || Number(totalPagesFromQuery);

  return (
    <div className={`grants-pagination ${loading ? "disabled" : ""}`}>
      {totalResults !== "0" && pageCount > 0 && (
        <Pagination
          aria-disabled={loading}
          pathname="/search"
          totalPages={pageCount}
          currentPage={page}
          maxSlots={MAX_SLOTS}
          onClickNext={() => updatePage(page + 1)}
          onClickPrevious={() => updatePage(page > 1 ? page - 1 : 0)}
          onClickPageNumber={(event: React.MouseEvent, page: number) =>
            updatePage(page)
          }
        />
      )}
    </div>
  );
}
