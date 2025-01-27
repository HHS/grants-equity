import { getAgenciesForFilterOptions } from "src/services/fetch/fetchers/agenciesFetcher";

import { useTranslations } from "next-intl";

import SearchFilterAccordion from "src/components/search/SearchFilterAccordion/SearchFilterAccordion";
import {
  categoryOptions,
  eligibilityOptions,
  fundingOptions,
} from "src/components/search/SearchFilterAccordion/SearchFilterOptions";
import SearchOpportunityStatus from "src/components/search/SearchOpportunityStatus";
import { AgencyFilterAccordion } from "./SearchFilterAccordion/AgencyFilterAccordion";

export default function SearchFilters({
  fundingInstrument,
  eligibility,
  agency,
  category,
  opportunityStatus,
}: {
  fundingInstrument: Set<string>;
  eligibility: Set<string>;
  agency: Set<string>;
  category: Set<string>;
  opportunityStatus: Set<string>;
}) {
  const t = useTranslations("Search");
  const agenciesPromise = getAgenciesForFilterOptions();

  return (
    <>
      <SearchOpportunityStatus query={opportunityStatus} />
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
        agencyOptionsPromise={agenciesPromise}
      />
      <SearchFilterAccordion
        filterOptions={categoryOptions}
        query={category}
        queryParamKey={"category"}
        title={t("accordion.titles.category")}
      />
    </>
  );
}
