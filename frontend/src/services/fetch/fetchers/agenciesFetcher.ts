"server only";

import { fetchAgencies } from "src/services/fetch/fetchers/fetchers";

import { FilterOption } from "src/components/search/SearchFilterAccordion/SearchFilterAccordion";

interface RelevantAgencyRecord {
  agency_code: string;
  agency_id: number;
  agency_name: string;
  sub_agency_code: string; // if this == agency_code then we're dealing with a potential for children
}

// would have called this getAgencies, but technically it's a POST
const obtainAgencies = async (): Promise<RelevantAgencyRecord[]> => {
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

export const agenciesToFilterOptions = (
  agencies: RelevantAgencyRecord[],
): FilterOption[] => {
  // this sort can be removed if ZXXXX is done and we make a change to do this sort on the API side
  const alphabeticalAgencies = agencies.sort((a, b) =>
    a.agency_name.localeCompare(b.agency_name),
  );
  // this should put all parent agencies at the top of the list
  const sortedAgencies = alphabeticalAgencies.sort((a, b) => {
    // when sub_agency_code == agency_code we know we're dealing with a parent agency
    if (a.sub_agency_code === a.agency_code) {
      return b.sub_agency_code === b.agency_code ? 0 : -1;
    }
    return b.sub_agency_code === b.agency_code ? 1 : 0;
  });
  return sortedAgencies.reduce((acc, rawAgency) => {
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

export const getAgenciesForFilterOptions = async (): Promise<
  FilterOption[]
> => {
  try {
    const agencies = await obtainAgencies();
    return agenciesToFilterOptions(agencies);
  } catch (e) {
    console.error("Error fetching agencies", e);
    return [];
  }
};
