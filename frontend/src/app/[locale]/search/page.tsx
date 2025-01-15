import { Metadata } from "next";
import QueryProvider from "src/app/[locale]/search/QueryProvider";
import withFeatureFlag from "src/hoc/withFeatureFlag";
import { LocalizedPageProps } from "src/types/intl";
import { SearchParamsTypes } from "src/types/search/searchRequestTypes";
import { Breakpoints } from "src/types/uiTypes";
import { convertSearchParamsToProperTypes } from "src/utils/search/convertSearchParamsToProperTypes";

import { useTranslations } from "next-intl";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { redirect } from "next/navigation";
import { use } from "react";

import ContentDisplayToggle from "src/components/ContentDisplayToggle";
import SearchAnalytics from "src/components/search/SearchAnalytics";
import SearchBar from "src/components/search/SearchBar";
import SearchFilters from "src/components/search/SearchFilters";
import SearchResults from "src/components/search/SearchResults";

export async function generateMetadata({ params }: LocalizedPageProps) {
  const { locale } = await params;
  const t = await getTranslations({ locale });
  const meta: Metadata = {
    title: t("Search.title"),
    description: t("Search.meta_description"),
  };
  return meta;
}
type SearchPageProps = {
  searchParams: Promise<SearchParamsTypes>;
  params: Promise<{ locale: string }>;
};

function Search({ searchParams, params }: SearchPageProps) {
  const { locale } = use(params);
  const searchParamsRead = use(searchParams);
  setRequestLocale(locale);
  const t = useTranslations("Search");

  const convertedSearchParams =
    convertSearchParamsToProperTypes(searchParamsRead);
  const { agency, category, eligibility, fundingInstrument, query, status } =
    convertedSearchParams;

  if (!("page" in searchParamsRead)) {
    searchParamsRead.page = "1";
  }

  return (
    <>
      <SearchAnalytics params={searchParamsRead} />
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
                type="centered"
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
            <div className="tablet:grid-col-8">
              <SearchResults
                searchParams={convertedSearchParams}
                query={query}
                loadingMessage={t("loading")}
              ></SearchResults>
            </div>
          </div>
        </div>
      </QueryProvider>
    </>
  );
}

// Exports page behind both feature flags
export default withFeatureFlag<SearchPageProps, never>(
  Search,
  "searchOff",
  () => redirect("/maintenance"),
);
