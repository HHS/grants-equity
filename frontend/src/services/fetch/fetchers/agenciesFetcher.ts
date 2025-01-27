"server only";

import { fetchAgencies } from "src/services/fetch/fetchers/fetchers";
import { sortFilterOptions } from "src/utils/search/searchUtils";

import { FilterOption } from "src/components/search/SearchFilterAccordion/SearchFilterAccordion";

export interface RelevantAgencyRecord {
  agency_code: string;
  agency_id: number;
  agency_name: string;
  sub_agency_code: string; // if this == agency_code then we're dealing with a potential for children
}

// would have called this getAgencies, but technically it's a POST
export const obtainAgencies = async (): Promise<RelevantAgencyRecord[]> => {
  const response = await fetchAgencies({
    body: {
      pagination: {
        order_by: "created_at", // this seems to be the only supported option
        page_offset: 1,
        page_size: 100, // should fetch them all. db seems to have 74 records as of 1/17/25
        sort_direction: "ascending",
      },
    },
  });
  return response.data as RelevantAgencyRecord[];
};

// translates API response containing flat list of agencies into nested filter options
export const agenciesToFilterOptions = (
  agencies: RelevantAgencyRecord[],
): FilterOption[] => {
  // this should put all parent agencies at the top of the list to make it simpler to nest
  const agenciesWithTopLevelAgenciesFloated = agencies.sort((a, b) => {
    // when sub_agency_code == agency_code we know we're dealing with a parent agency
    if (a.sub_agency_code === a.agency_code) {
      return b.sub_agency_code === b.agency_code ? 0 : -1;
    }
    return b.sub_agency_code === b.agency_code ? 1 : 0;
  });

  return agenciesWithTopLevelAgenciesFloated.reduce((acc, rawAgency) => {
    const agencyOption = {
      id: rawAgency.agency_code,
      label: rawAgency.agency_name,
      value: rawAgency.agency_code,
    };
    if (
      !rawAgency.sub_agency_code ||
      rawAgency.sub_agency_code === rawAgency.agency_code
    ) {
      return [...acc, agencyOption];
    }
    const parent = acc.find(
      (agency: FilterOption) => agency.id === rawAgency.sub_agency_code,
    );
    // parent should always exist because of the pre-sort
    if (!parent) {
      throw new Error(`Parent agency not found: ${rawAgency.sub_agency_code}`);
    }
    if (!parent.children) {
      parent.children = [];
    }
    parent.children.push(agencyOption);
    return acc;
  }, [] as FilterOption[]);
};

export const getAgenciesForFilterOptions = async (
  prefetchedOptions?: FilterOption[],
): Promise<FilterOption[]> => {
  try {
    if (prefetchedOptions) {
      return Promise.resolve(prefetchedOptions);
    }
    const agencies = await obtainAgencies();
    const filterOptions = agenciesToFilterOptions(agencies);
    return sortFilterOptions(filterOptions);
  } catch (e) {
    console.error("Error fetching agencies", e);
    return [];
  }
};
