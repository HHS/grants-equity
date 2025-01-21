import { getAgenciesForFilterOptions } from "src/services/fetch/fetchers/agenciesFetcher";

import { useTranslations } from "next-intl";
import { Suspense } from "react";
import { Accordion } from "@trussworks/react-uswds";

import SearchFilterAccordion, {
  FilterAccordionProps,
  FilterOption,
} from "src/components/search/SearchFilterAccordion/SearchFilterAccordion";
import {
  categoryOptions,
  eligibilityOptions,
  fundingOptions,
} from "src/components/search/SearchFilterAccordion/SearchFilterOptions";
import SearchOpportunityStatus from "src/components/search/SearchOpportunityStatus";

interface FetchedOptionsFilterAccordionProps extends FilterAccordionProps {
  filterOptionsPromise: Promise<FilterOption[]>;
}

// async component used to handle fetching agencies
export async function FetchedOptionsFilterAccordion({
  filterOptionsPromise,
  title,
  queryParamKey,
  query,
}: FetchedOptionsFilterAccordionProps) {
  const filterOptions = await filterOptionsPromise;
  return (
    <SearchFilterAccordion
      filterOptions={filterOptions}
      query={query}
      queryParamKey={queryParamKey}
      title={title}
    />
  );
}

// TODO: disabled styling for suspended component
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
      <Suspense
        fallback={
          <Accordion
            bordered={true}
            items={[
              {
                title: `${t("accordion.titles.agency")}`,
                content: [],
                expanded: false,
                id: `opportunity-filter-agency-disabled`,
                headingLevel: "h2",
              },
            ]}
            multiselectable={true}
            className="margin-top-4"
          />
        }
      >
        <FetchedOptionsFilterAccordion
          filterOptionsPromise={agenciesPromise}
          query={agency}
          queryParamKey={"agency"}
          title={t("accordion.titles.agency")}
        />
      </Suspense>
      <SearchFilterAccordion
        filterOptions={categoryOptions}
        query={category}
        queryParamKey={"category"}
        title={t("accordion.titles.category")}
      />
    </>
  );
}
