import {
  agenciesToFilterOptions,
  getAgenciesForFilterOptions,
  obtainAgencies,
  RelevantAgencyRecord,
} from "src/services/fetch/fetchers/agenciesFetcher";

const fakeAgencyResponseData: RelevantAgencyRecord[] = [
  {
    agency_code: "DOC-NIST",
    agency_name: "National Institute of Standards and Technology",
    sub_agency_code: "DOC-NIST",
    agency_id: 1,
  },
  {
    agency_code: "MOCK-NIST",
    agency_name: "Mational Institute",
    sub_agency_code: "MOCK-NIST",
    agency_id: 1,
  },
  {
    agency_code: "MOCK-TRASH",
    agency_name: "Mational TRASH",
    sub_agency_code: "MOCK-TRASH",
    agency_id: 1,
  },
  {
    agency_code: "FAKE",
    agency_name: "Completely fake",
    sub_agency_code: "FAKE",
    agency_id: 1,
  },
];

const mockfetchAgencies = jest
  .fn()
  .mockResolvedValue({ data: fakeAgencyResponseData });
const mockSortFilterOptions = jest.fn();

jest.mock("src/services/fetch/fetchers/fetchers", () => ({
  fetchAgencies: (arg: unknown): unknown => mockfetchAgencies(arg),
}));

jest.mock("src/utils/search/searchUtils", () => ({
  sortFilterOptions: (arg: unknown): unknown => mockSortFilterOptions(arg),
}));

describe("obtainAgencies", () => {
  it("calls request function with correct parameters", async () => {
    const result = await obtainAgencies();

    expect(mockfetchAgencies).toHaveBeenCalledWith({
      body: {
        pagination: {
          order_by: "created_at", // this seems to be the only supported option
          page_offset: 1,
          page_size: 100, // should fetch them all. db seems to have 74 records as of 1/17/25
          sort_direction: "ascending",
        },
      },
    });

    expect(result).toEqual(fakeAgencyResponseData);
  });
});

describe("agenciesToFilterOptions", () => {
  it("converts a simple list of top level agencies to filter options", () => {
    expect(agenciesToFilterOptions(fakeAgencyResponseData)).toEqual([
      {
        id: "DOC-NIST",
        label: "National Institute of Standards and Technology",
        value: "DOC-NIST",
      },
      {
        id: "MOCK-NIST",
        label: "Mational Institute",
        value: "MOCK-NIST",
      },
      {
        id: "MOCK-TRASH",
        label: "Mational TRASH",
        value: "MOCK-TRASH",
      },
      {
        id: "FAKE",
        label: "Completely fake",
        value: "FAKE",
      },
    ]);
  });

  it("converts a complex list of nested agencies to filter options", () => {
    const fakeAgencyResponseData: RelevantAgencyRecord[] = [
      {
        agency_code: "DOC-NIST",
        agency_name: "National Institute of Standards and Technology",
        sub_agency_code: "DOC-NIST",
        agency_id: 1,
      },
      {
        agency_code: "HI",
        agency_name: "Hello",
        sub_agency_code: "DOC-NIST",
        agency_id: 1,
      },
      {
        agency_code: "MOCK-NIST",
        agency_name: "Mational Institute",
        sub_agency_code: "MOCK-NIST",
        agency_id: 1,
      },
      {
        agency_code: "TRASH",
        agency_name: "More TRASH",
        sub_agency_code: "MOCK-TRASH",
        agency_id: 1,
      },
      {
        agency_code: "MOCK-TRASH",
        agency_name: "Mational TRASH",
        sub_agency_code: "MOCK-TRASH",
        agency_id: 1,
      },
      {
        agency_code: "FAKE",
        agency_name: "Completely fake",
        sub_agency_code: "FAKE",
        agency_id: 1,
      },
      {
        agency_code: "There",
        agency_name: "Again",
        sub_agency_code: "DOC-NIST",
        agency_id: 1,
      },
    ];
    expect(agenciesToFilterOptions(fakeAgencyResponseData)).toEqual([
      {
        id: "DOC-NIST",
        label: "National Institute of Standards and Technology",
        value: "DOC-NIST",
        children: [
          {
            id: "HI",
            label: "Hello",
            value: "HI",
          },
          {
            id: "There",
            label: "Again",
            value: "There",
          },
        ],
      },
      {
        id: "MOCK-NIST",
        label: "Mational Institute",
        value: "MOCK-NIST",
      },
      {
        id: "MOCK-TRASH",
        label: "Mational TRASH",
        value: "MOCK-TRASH",
        children: [
          {
            id: "TRASH",
            label: "More TRASH",
            value: "TRASH",
          },
        ],
      },
      {
        id: "FAKE",
        label: "Completely fake",
        value: "FAKE",
      },
    ]);
  });
});

describe("getAgenciesForFilterOptions", () => {
  it("immediately returns prefetched agencies if supplied", async () => {
    const prefetchedOptions = [
      {
        id: "DOC-NIST",
        label: "National Institute of Standards and Technology",
        value: "DOC-NIST",
      },
      {
        id: "MOCK-NIST",
        label: "Mational Institute",
        value: "MOCK-NIST",
      },
      {
        id: "MOCK-TRASH",
        label: "Mational TRASH",
        value: "MOCK-TRASH",
      },
      {
        id: "FAKE",
        label: "Completely fake",
        value: "FAKE",
      },
    ];
    const result = await getAgenciesForFilterOptions(prefetchedOptions);
    expect(result).toEqual(prefetchedOptions);
  });
  it("sorts", async () => {
    await getAgenciesForFilterOptions();
    expect(mockSortFilterOptions).toHaveBeenCalledWith([
      {
        id: "DOC-NIST",
        label: "National Institute of Standards and Technology",
        value: "DOC-NIST",
      },
      {
        id: "MOCK-NIST",
        label: "Mational Institute",
        value: "MOCK-NIST",
      },
      {
        id: "MOCK-TRASH",
        label: "Mational TRASH",
        value: "MOCK-TRASH",
      },
      {
        id: "FAKE",
        label: "Completely fake",
        value: "FAKE",
      },
    ]);
  });
});
