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
