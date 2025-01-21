import { useTranslations } from "next-intl";
import { Suspense } from "react";
import { Accordion } from "@trussworks/react-uswds";

import SearchFilterAccordion, {
  FilterOption,
} from "src/components/search/SearchFilterAccordion/SearchFilterAccordion";

// this could be abstracted if we ever want to do this again
export async function AgencyFilterAccordion({
  query,
  agenciesPromise,
}: {
  query: Set<string>;
  agenciesPromise: Promise<FilterOption[]>;
}) {
  const t = useTranslations("Search");
  const agencies = await agenciesPromise;
  return (
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
      <SearchFilterAccordion
        filterOptions={agencies}
        query={query}
        queryParamKey={"agency"}
        title={t("accordion.titles.agency")}
      />
    </Suspense>
  );
}
