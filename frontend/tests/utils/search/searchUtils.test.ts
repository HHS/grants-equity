import { sortFilterOptions } from "src/utils/search/searchUtils";

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
