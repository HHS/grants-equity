/**
 * @jest-environment node
 */

import { GET } from "src/app/api/search/export/route";

import { NextRequest } from "next/server";

const fakeRequestForSearchParams = (searchParams: string) => {
  return {
    nextUrl: {
      searchParams: new URLSearchParams(searchParams),
    },
  } as NextRequest;
};

const fakeConvertedParams = {
  actionType: "initialLoad",
  agency: new Set(["EPA"]),
  category: new Set(),
  eligibility: new Set(),
  fundingInstrument: new Set(),
  page: 1,
  query: "",
  sortby: null,
  status: new Set(["closed"]),
};

const mockDownloadOpportunities = jest.fn((params: unknown): unknown => params);

jest.mock("src/services/fetch/fetchers/searchFetcher", () => ({
  downloadOpportunities: (params: unknown) => mockDownloadOpportunities(params),
}));

jest.mock("next/server", () => ({
  NextResponse: jest.fn((params: unknown): unknown => ({
    calledWith: params,
  })),
}));

// note that all calls to the GET endpoint need to be caught here since the behavior of the Next redirect
// is to throw an error
describe("search export GET request", () => {
  afterEach(() => jest.clearAllMocks());
  it("calls downloadOpportunities with expected arguments", async () => {
    await GET(fakeRequestForSearchParams("status=closed&agency=EPA"));
    expect(mockDownloadOpportunities).toHaveBeenCalledWith(fakeConvertedParams);
  });

  it("returns a new response created from the returned value of downloadOpportunties", async () => {
    const response = await GET(
      fakeRequestForSearchParams("status=closed&agency=EPA"),
    );
    expect(response).toEqual({
      calledWith: fakeConvertedParams,
    });
  });
});
