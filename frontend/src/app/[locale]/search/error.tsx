"use client";

import QueryProvider from "src/app/[locale]/search/QueryProvider";
import { FrontendErrorDetails } from "src/types/apiResponseTypes";
import { ServerSideSearchParams } from "src/types/searchRequestURLTypes";
import { Breakpoints, ErrorProps } from "src/types/uiTypes";
import { convertSearchParamsToProperTypes } from "src/utils/search/convertSearchParamsToProperTypes";

import { useTranslations } from "next-intl";
import { useSearchParams } from "next/navigation";
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

/*
  - expand the layout to ensure that server side rendering can happen on the agency filter
  - - problem is that then we would not be able to repopulate the form state on error
  - mock out the agency list based on hardcoded options
  - - this just seems like a bad hack, and we have to bloat our payload with bad data
  - - also the inconsistency would be very confusing
  - explicitly stash the agency list in local storage and retrieve it here?
  - - probably creating a local storage provider in the layout is a good idea, and we can use it to store the agency list for use here
  - - we'll also need to restructure the filters to support pulling from local storage instead of the API (since we just pass a promise containing the agencies down, maybe it's enough to make how we create that promise more flexible)
*/

export default function SearchError({ error }: ErrorProps) {
  const t = useTranslations("Search");

  const searchParams = useSearchParams();
  const convertedSearchParams = convertSearchParamsToProperTypes(
    Object.fromEntries(searchParams.entries().toArray()),
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
            {/* <ContentDisplayToggle
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
            </ContentDisplayToggle> */}
          </div>
          <div className="tablet:grid-col-8">{ErrorAlert}</div>
        </div>
      </div>
    </QueryProvider>
  );
}
