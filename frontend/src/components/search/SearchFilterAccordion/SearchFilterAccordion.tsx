"use client";

import { camelCase } from "lodash";
import { QueryContext } from "src/app/[locale]/search/QueryProvider";
import { useSearchParamUpdater } from "src/hooks/useSearchParamUpdater";
import { useGlobalState } from "src/services/globalState/GlobalStateProvider";
import { QueryParamKey } from "src/types/search/searchResponseTypes";

import { useContext, useEffect } from "react";
import { Accordion } from "@trussworks/react-uswds";

import SearchFilterCheckbox from "src/components/search/SearchFilterAccordion/SearchFilterCheckbox";
import SearchFilterSection from "src/components/search/SearchFilterAccordion/SearchFilterSection/SearchFilterSection";
import SearchFilterToggleAll from "src/components/search/SearchFilterAccordion/SearchFilterToggleAll";

export interface AccordionItemProps {
  title: React.ReactNode | string;
  content: React.ReactNode;
  expanded: boolean;
  id: string;
  headingLevel: "h1" | "h2" | "h3" | "h4" | "h5" | "h6";
  className?: string;
}

export interface FilterOption {
  children?: FilterOption[];
  id: string;
  isChecked?: boolean;
  label: string;
  value: string;
}

export interface SearchFilterAccordionProps {
  query: Set<string>;
  queryParamKey: QueryParamKey; // Ex - In query params, search?{key}=first,second,third
  title: string; // Title in header of accordion
  filterOptions: FilterOption[];
}

export interface FilterOptionWithChildren {
  id: string;
  label: string;
  value: string;
  isChecked?: boolean;
  children: FilterOption[];
}

const isSectionAllSelected = (
  allSelected: Set<string>,
  query: Set<string>,
): boolean => {
  return areSetsEqual(allSelected, query);
};

const isSectionNoneSelected = (query: Set<string>): boolean => {
  return query.size === 0;
};

const areSetsEqual = (a: Set<string>, b: Set<string>) =>
  a.size === b.size && [...a].every((value) => b.has(value));

export function SearchFilterAccordion({
  filterOptions,
  title,
  queryParamKey,
  query,
}: SearchFilterAccordionProps) {
  const { queryTerm } = useContext(QueryContext);
  const { updateQueryParams, searchParams } = useSearchParamUpdater();
  const { setAgencyOptions } = useGlobalState(({ setAgencyOptions }) => ({
    setAgencyOptions,
  }));

  useEffect(() => {
    if (queryParamKey === "agency" && filterOptions && setAgencyOptions) {
      setAgencyOptions(filterOptions);
    }
  }, [queryParamKey, filterOptions, setAgencyOptions]);

  const totalCheckedCount = query.size;
  // all top level selectable filter options
  const allOptionValues = filterOptions.reduce((values: string[], option) => {
    if (option.children) {
      return values;
    }
    values.push(option.value);
    return values;
  }, []);

  const allSelected = new Set(allOptionValues);

  // SPLIT ME INTO MY OWN COMPONENT
  const getAccordionTitle = () => (
    <>
      {title}
      {!!totalCheckedCount && (
        <span className="usa-tag usa-tag--big radius-pill margin-left-1">
          {totalCheckedCount}
        </span>
      )}
    </>
  );

  // need to add any existing relevant search params to the passed in set
  const toggleSelectAll = (all: boolean, newSelections?: Set<string>): void => {
    if (all && newSelections) {
      // get existing current selected options for this accordion from url
      const currentSelections = new Set(
        searchParams.get(camelCase(title))?.split(","),
      );
      // add existing to newly selected section
      const sectionPlusCurrent = new Set([
        ...currentSelections,
        ...newSelections,
      ]);
      updateQueryParams(sectionPlusCurrent, queryParamKey, queryTerm);
    } else {
      const clearedSelections = newSelections || new Set<string>();
      updateQueryParams(clearedSelections, queryParamKey, queryTerm);
    }
  };

  const toggleOptionChecked = (value: string, isChecked: boolean) => {
    const updated = new Set(query);
    isChecked ? updated.add(value) : updated.delete(value);
    updateQueryParams(updated, queryParamKey, queryTerm);
  };

  const isExpanded = !!query.size;

  // SPLIT ME INTO MY OWN COMPONENT
  const getAccordionContent = () => (
    <>
      <SearchFilterToggleAll
        onSelectAll={() => toggleSelectAll(true, allSelected)}
        onClearAll={() => toggleSelectAll(false)}
        isAllSelected={isSectionAllSelected(allSelected, query)}
        isNoneSelected={isSectionNoneSelected(query)}
      />

      <ul className="usa-list usa-list--unstyled">
        {filterOptions.map((option) => (
          <li key={option.id}>
            {/* If we have children, show a "section" dropdown, otherwise show just a checkbox */}
            {option.children ? (
              // SearchFilterSection will map over all children of this option
              <SearchFilterSection
                option={option as FilterOptionWithChildren}
                value={option.value}
                query={query}
                updateCheckedOption={toggleOptionChecked}
                toggleSelectAll={toggleSelectAll}
                accordionTitle={title}
                isSectionAllSelected={isSectionAllSelected}
                isSectionNoneSelected={isSectionNoneSelected}
              />
            ) : (
              <SearchFilterCheckbox
                option={option}
                query={query}
                updateCheckedOption={toggleOptionChecked}
                accordionTitle={title}
              />
            )}
          </li>
        ))}
      </ul>
    </>
  );

  // MEMOIZE ME
  const accordionOptions: AccordionItemProps[] = [
    {
      title: getAccordionTitle(),
      content: getAccordionContent(),
      expanded: isExpanded,
      id: `opportunity-filter-${queryParamKey}`,
      headingLevel: "h2",
    },
  ];

  return (
    <Accordion
      bordered={true}
      items={accordionOptions}
      multiselectable={true}
      className="margin-top-4"
    />
  );
}

export default SearchFilterAccordion;
