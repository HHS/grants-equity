"use client";

import QueryProvider from "src/app/[locale]/search/QueryProvider";
import { useGlobalState } from "src/services/globalState/GlobalStateProvider";
import { FrontendErrorDetails } from "src/types/apiResponseTypes";
import { ServerSideSearchParams } from "src/types/searchRequestURLTypes";
import { Breakpoints, ErrorProps } from "src/types/uiTypes";
import { convertSearchParamsToProperTypes } from "src/utils/search/convertSearchParamsToProperTypes";
import { isvalidj }

import { useTranslations } from "next-intl";
import { useSearchParams } from "next/navigation";
import { useEffect } from "react";
import { Alert } from "@trussworks/react-uswds";

import ContentDisplayToggle from "src/components/ContentDisplayToggle";
import SearchBar from "src/components/search/SearchBar";
import { AgencyFilterAccordion } from "src/components/search/SearchFilterAccordion/AgencyFilterAccordion";
import SearchFilterAccordion from "src/components/search/SearchFilterAccordion/SearchFilterAccordion";
import {
  categoryOptions,
  eligibilityOptions,
  fundingOptions,
} from "src/components/search/SearchFilterAccordion/SearchFilterOptions";
import SearchOpportunityStatus from "src/components/search/SearchOpportunityStatus";
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

// note that the SearchFilters component is not used since it is a server component
// we work around that by including the rendered components from SearchFilters, but manually
// passing through the agency options as received from global state rather than fetching from API
export default function SearchError({ error }: ErrorProps) {
  const t = useTranslations("Search");

  const searchParams = useSearchParams();
  useEffect(() => {
    console.error(error);
  }, [error]);

  // const { agencyOptions } = useMemo(
  //   () =>
  //     useGlobalState(({ agencyOptions }) => ({
  //       agencyOptions,
  //     })),
  //   [],
  // );

  const parsedErrorData = isValidJSON(error.message) ? JSON.parse(error.message) : {}

  const { agencyOptions } = useGlobalState(({ agencyOptions }) => ({
    agencyOptions,
  }));

  // const agencyOptions = [];
  const convertedSearchParams = convertSearchParamsToProperTypes(
    Object.fromEntries(searchParams.entries().toArray()),
  );

  const { agency, category, eligibility, fundingInstrument, query, status } =
    convertedSearchParams;

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
              <SearchOpportunityStatus query={status} />
              <SearchFilterAccordion
                filterOptions={fundingOptions}
                query={fundingInstrument}
                queryParamKey="fundingInstrument"
                title={t("accordion.titles.funding")}
              />
              <SearchFilterAccordion
                filterOptions={eligibilityOptions}
                query={eligibility}
                queryParamKey={"eligibility"}
                title={t("accordion.titles.eligibility")}
              />
              <AgencyFilterAccordion
                query={agency}
                agencyOptions={agencyOptions}
              />
              <SearchFilterAccordion
                filterOptions={categoryOptions}
                query={category}
                queryParamKey={"category"}
                title={t("accordion.titles.category")}
              />
            </ContentDisplayToggle>
          </div>
          <div className="tablet:grid-col-8">{ErrorAlert}</div>
        </div>
      </div>
    </QueryProvider>
  );
}
