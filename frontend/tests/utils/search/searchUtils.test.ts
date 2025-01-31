import { Opportunity } from "src/types/search/searchResponseTypes";
import {
  lookUpAgencyName,
  sortFilterOptions,
} from "src/utils/search/searchUtils";

describe("sortFilterOptions", () => {
  it("alphabetically sorts top level and child options by label", () => {
    expect(
      sortFilterOptions([
        {
          id: "NARA",
          label: "National Archives and Records Administration",
          value: "NARA",
        },
        {
          id: "HUD",
          label: "Department of Housing and Urban Development",
          value: "HUD",
        },
        {
          id: "DOE",
          label: "Department of Energy",
          value: "DOE",
          children: [
            {
              id: "DOE-GFO",
              label: "Golden Field Office",
              value: "DOE-GFO",
            },
            {
              id: "DOE-NETL",
              label: "National Energy Technology Laboratory",
              value: "DOE-NETL",
            },
            {
              id: "DOE-ID",
              label: "Idaho Field Office",
              value: "DOE-ID",
            },
            {
              id: "DOE-CH",
              label: "Chicago Service Center",
              value: "DOE-CH",
            },
          ],
        },
        {
          id: "NASA",
          label: "National Aeronautics and Space Administration",
          value: "NASA",
          children: [
            {
              id: "NASA-GSFC",
              label: "NASA Goddard Space Flight Center",
              value: "NASA-GSFC",
            },
            {
              id: "NASA-HQ",
              label: "NASA Headquarters",
              value: "NASA-HQ",
            },
          ],
        },
      ]),
    ).toEqual([
      {
        id: "DOE",
        label: "Department of Energy",
        value: "DOE",
        children: [
          {
            id: "DOE-CH",
            label: "Chicago Service Center",
            value: "DOE-CH",
          },
          {
            id: "DOE-GFO",
            label: "Golden Field Office",
            value: "DOE-GFO",
          },
          {
            id: "DOE-ID",
            label: "Idaho Field Office",
            value: "DOE-ID",
          },
          {
            id: "DOE-NETL",
            label: "National Energy Technology Laboratory",
            value: "DOE-NETL",
          },
        ],
      },
      {
        id: "HUD",
        label: "Department of Housing and Urban Development",
        value: "HUD",
      },
      {
        id: "NASA",
        label: "National Aeronautics and Space Administration",
        value: "NASA",
        children: [
          {
            id: "NASA-GSFC",
            label: "NASA Goddard Space Flight Center",
            value: "NASA-GSFC",
          },
          {
            id: "NASA-HQ",
            label: "NASA Headquarters",
            value: "NASA-HQ",
          },
        ],
      },
      {
        id: "NARA",
        label: "National Archives and Records Administration",
        value: "NARA",
      },
    ]);
  });
});

describe("lookUpAgencyName", () => {
  const fakeOpportunity = {
    agency: "NON-HMN-READABWOL",
    summary: {
      estimated_total_program_funding: 5000000,
      expected_number_of_awards: 10,
      award_ceiling: 1000000,
      award_floor: 50000,
      is_cost_sharing: true,
      funding_instruments: ["Grant", "Cooperative Agreement"],
      funding_categories: ["Education", "Health"],
      funding_category_description:
        "Support for education and health initiatives",
    },
    category: "Discretionary",
    category_explanation: "Funds allocated by agency discretion",
  } as Opportunity;

  const agencyListItem = {
    value: "NON-HMN-READABWOL",
    id: "NON-HMN-READABWOL",
    label: "Nice Agency Name",
  };

  it("returns `--` if agency lookup fails", () => {
    expect(
      lookUpAgencyName(fakeOpportunity, [
        { ...agencyListItem, value: "EXTRA-NON-HMN-READABWOL" },
      ]),
    ).toEqual("--");
  });

  it("finds agency and returns label (agency)", () => {
    expect(lookUpAgencyName(fakeOpportunity, [agencyListItem])).toEqual(
      "Nice Agency Name",
    );
  });
  it("finds agency and returns label (summary)", () => {
    expect(
      lookUpAgencyName(
        {
          ...fakeOpportunity,
          agency: null,
          summary: {
            ...fakeOpportunity.summary,
            agency_code: "NON-HMN-READABWOL",
          },
        },
        [agencyListItem],
      ),
    ).toEqual("Nice Agency Name");
  });
  it("does not find nested agencies", () => {
    expect(
      lookUpAgencyName(fakeOpportunity, [
        {
          ...agencyListItem,
          value: "sometihng else",
          children: [agencyListItem],
        },
      ]),
    ).toEqual("--");
  });
});
