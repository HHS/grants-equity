"use client";

import { useSearchParams } from "next/navigation";
import { createContext, useCallback, useMemo, useState } from "react";

export interface QueryContextParams {
  queryTerm: string | null | undefined;
  updateQueryTerm: (term: string) => void;
  totalPages: string | null | undefined;
  updateTotalPages: (page: string) => void;
  totalResults: string;
  updateTotalResults: (total: string) => void;
}

export const QueryContext = createContext({} as QueryContextParams);

export default function QueryProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const searchParams = useSearchParams() || undefined;
  const defaultTerm = searchParams?.get("query");
  const [queryTerm, setQueryTerm] = useState(defaultTerm);
  const [totalPages, setTotalPages] = useState("na");
  const [totalResults, setTotalResults] = useState("");

  const updateQueryTerm = useCallback((term: string) => {
    setQueryTerm(term);
  }, []);

  const updateTotalResults = useCallback((total: string) => {
    setTotalResults(total);
  }, []);

  const updateTotalPages = useCallback((page: string) => {
    setTotalPages(page);
  }, []);

  const contextValue = useMemo(
    () => ({
      queryTerm,
      updateQueryTerm,
      totalPages,
      updateTotalPages,
      totalResults,
      updateTotalResults,
    }),
    [
      queryTerm,
      updateQueryTerm,
      totalPages,
      updateTotalPages,
      totalResults,
      updateTotalResults,
    ],
  );

  return (
    <QueryContext.Provider value={contextValue}>
      {children}
    </QueryContext.Provider>
  );
}
