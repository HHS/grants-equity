import { useTranslations } from "next-intl";
import { Suspense } from "react";
import { Accordion } from "@trussworks/react-uswds";

import SearchFilterAccordion, {
  FilterOption,
} from "src/components/search/SearchFilterAccordion/SearchFilterAccordion";

async function AgencyFilterAccordionWithFetchedOptions({
  query,
  agenciesPromise,
  title,
}: {
  query: Set<string>;
  agenciesPromise: Promise<FilterOption[]>;
  title: string;
}) {
  const agencies = await agenciesPromise;
  return (
    <SearchFilterAccordion
      filterOptions={agencies}
      query={query}
      queryParamKey={"agency"}
      title={title}
    />
  );
}

// functionality differs depending on whether `agencyOptions` or `agencyOptionsPromise` is passed
// with prefetched options we have a synchronous render
// with a Promise we have an async render with Suspense
export function AgencyFilterAccordion({
  query,
  agencyOptions,
  agencyOptionsPromise,
}: {
  query: Set<string>;
  agencyOptions?: FilterOption[];
  agencyOptionsPromise?: Promise<FilterOption[]>;
}) {
  const t = useTranslations("Search");
  const title = t("accordion.titles.agency");
  if (agencyOptions) {
    return (
      <SearchFilterAccordion
        filterOptions={agencyOptions}
        query={query}
        queryParamKey={"agency"}
        title={title}
      />
    );
  }
  if (agencyOptionsPromise) {
    return (
      <Suspense
        fallback={
          <Accordion
            bordered={true}
            items={[
              {
                title,
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
        <AgencyFilterAccordionWithFetchedOptions
          agenciesPromise={agencyOptionsPromise}
          query={query}
          title={title}
        />
      </Suspense>
    );
  }
  throw new Error(
    "AgencyFilterAccordion must have either agencyOptions or agencyOptionsPromise prop",
  );
}
