import { getOpportunityDetails } from "src/services/fetch/fetchers/opportunityFetcher";

const fakeResponseBody = { some: "response body" };
const mockJson = jest.fn(() => fakeResponseBody);

const mockfetchOpportunity = jest.fn().mockResolvedValue({
  json: mockJson,
});

jest.mock("src/services/fetch/fetchers/fetchers", () => ({
  fetchOpportunity: (params: unknown): unknown => {
    return mockfetchOpportunity(params);
  },
}));

describe("getOpportunityDetails", () => {
  afterEach(() => jest.clearAllMocks());
  it("calls fetchOpportunity with the correct arguments", async () => {
    await getOpportunityDetails("an id");
    expect(mockfetchOpportunity).toHaveBeenCalledWith({ subPath: "an id" });
  });

  it("returns json from response", async () => {
    const result = await getOpportunityDetails("an id");
    expect(mockJson).toHaveBeenCalledTimes(1);
    expect(result).toEqual(fakeResponseBody);
  });
});
