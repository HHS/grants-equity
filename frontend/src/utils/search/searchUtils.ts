import { Opportunity } from "src/types/search/searchResponseTypes";

import { FilterOption } from "src/components/search/SearchFilterAccordion/SearchFilterAccordion";

export const alphabeticalOptionSort = (
  firstOption: FilterOption,
  secondOption: FilterOption,
) => firstOption.label.localeCompare(secondOption.label);

// alphabetically sorts nested and top level filter options
export const sortFilterOptions = (
  filterOptions: FilterOption[],
): FilterOption[] => {
  const childrenSorted = filterOptions.map((option) => {
    if (option.children) {
      return {
        ...option,
        children: option.children.toSorted(alphabeticalOptionSort),
      };
    }
    return option;
  });
  return childrenSorted.toSorted(alphabeticalOptionSort);
};

// finds human readable agency name by agency code in list of agency filter options
// agency options will come in pre-flattened
export const lookUpAgencyName = (
  opportunity: Opportunity,
  agencyOptions: FilterOption[],
): string => {
  const match = agencyOptions.find(
    (option) =>
      option.value === opportunity.agency ||
      option.value === opportunity.summary.agency_code,
  );
  return match?.label || "--";
};
