"use client";

import QueryProvider from "src/app/[locale]/search/QueryProvider";
import { usePrevious } from "src/hooks/usePrevious";
import { FrontendErrorDetails } from "src/types/apiResponseTypes";
import { ServerSideSearchParams } from "src/types/searchRequestURLTypes";
import { Breakpoints, ErrorProps } from "src/types/uiTypes";
import { convertSearchParamsToProperTypes } from "src/utils/search/convertSearchParamsToProperTypes";

import { useTranslations } from "next-intl";
import { ReadonlyURLSearchParams, useSearchParams } from "next/navigation";
import { useEffect } from "react";
import { Alert } from "@trussworks/react-uswds";

import ContentDisplayToggle from "src/components/ContentDisplayToggle";
import SearchBar from "src/components/search/SearchBar";
import SearchFilters from "src/components/search/SearchFilters";
import ServerErrorAlert from "src/components/ServerErrorAlert";

export interface ParsedError {
  message: string;
  searchInputs: ServerSideSearchParams;
  status: number;
  type: string;
  details?: FrontendErrorDetails;
}

function isValidJSON(str: string) {
  try {
    JSON.parse(str);
    return true;
  } catch (e) {
    return false; // String is not valid JSON
  }
}

function createBlankParsedError(): ParsedError {
  return {
    type: "NetworkError",
    searchInputs: {
      query: "",
      status: "",
      fundingInstrument: "",
      eligibility: "",
      agency: "",
      category: "",
      sortby: undefined,
      page: "1",
      actionType: "initialLoad",
    },
    message: "Invalid error message JSON returned",
    status: -1,
  };
}

export default function SearchError({ error, reset }: ErrorProps) {
  const t = useTranslations("Search");
  const searchParams = useSearchParams();
  const previousSearchParams =
    usePrevious<ReadonlyURLSearchParams>(searchParams);

  useEffect(() => {
    if (
      reset &&
      previousSearchParams &&
      searchParams.toString() !== previousSearchParams?.toString()
    ) {
      reset();
    }
  }, [searchParams, reset]);

  useEffect(() => {
    console.error(error);
  }, [error]);

  // The error message is passed as an object that's been stringified.
  // Parse it here.
  let parsedErrorData;

  if (!isValidJSON(error.message)) {
    // the error likely is just a string with a non-specific Server Component error when running the built app
    // "An error occurred in the Server Components render. The specific message is omitted in production builds..."
    parsedErrorData = createBlankParsedError();
  } else {
    // Valid error thrown from server component
    parsedErrorData = JSON.parse(error.message) as ParsedError;
  }
  const convertedSearchParams = convertSearchParamsToProperTypes(
    parsedErrorData.searchInputs,
  );
  const { agency, category, eligibility, fundingInstrument, query, status } =
    convertedSearchParams;

  useEffect(() => {
    console.error(error);
  }, [error]);

  // note that the validation error will contain untranslated strings
  const ErrorAlert =
    parsedErrorData.details && parsedErrorData.type === "ValidationError" ? (
      <Alert type="error" heading={t("validationError")} headingLevel="h4">
        {`Error in ${parsedErrorData.details.field || "a search field"}: ${parsedErrorData.details.message || "adjust your search and try again"}`}
      </Alert>
    ) : (
      <ServerErrorAlert callToAction={t("generic_error_cta")} />
    );

  return (
    <QueryProvider>
      <div className="grid-container">
        <div className="search-bar">
          <SearchBar query={query} />
        </div>
        <div className="grid-row grid-gap">
          <div className="tablet:grid-col-4">
            <ContentDisplayToggle
              showCallToAction={t("filterDisplayToggle.showFilters")}
              hideCallToAction={t("filterDisplayToggle.hideFilters")}
              breakpoint={Breakpoints.TABLET}
            >
              <SearchFilters
                opportunityStatus={status}
                eligibility={eligibility}
                category={category}
                fundingInstrument={fundingInstrument}
                agency={agency}
              />
            </ContentDisplayToggle>
          </div>
          <div className="tablet:grid-col-8">{ErrorAlert}</div>
        </div>
      </div>
    </QueryProvider>
  );
}
