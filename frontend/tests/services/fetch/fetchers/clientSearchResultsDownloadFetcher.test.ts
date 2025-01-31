/* eslint-disable @typescript-eslint/unbound-method */

import { downloadSearchResultsCSV } from "src/services/fetch/fetchers/clientSearchResultsDownloadFetcher";
import { getConfiguredDayJs } from "src/utils/dateUtil";

import { ReadonlyURLSearchParams } from "next/navigation";

const fakeBlob = new Blob();

const getFakeFile = () =>
  new File(
    [fakeBlob],
    `grants-search-${getConfiguredDayJs()(new Date()).format("YYYYMMDDHHmm")}.csv`,
    {
      type: "data:text/csv",
    },
  );

const mockBlob = jest.fn(() => fakeBlob);

const mockFetch = jest.fn(() =>
  Promise.resolve({
    blob: mockBlob,
    ok: true,
  }),
);
const mockCreateObjectUrl = jest.fn(() => "an object url");
const mockLocationAssign = jest.fn();

describe("downloadSearchResultsCSV", () => {
  let originalFetch: typeof global.fetch;
  let originalCreateObjectURL: typeof global.URL.createObjectURL;
  let originalLocationAssign: typeof global.location.assign;

  beforeEach(() => {
    originalCreateObjectURL = global.URL.createObjectURL;
    originalLocationAssign = global.location.assign;
    Object.defineProperty(global, "location", {
      value: { assign: mockLocationAssign },
    });
    originalFetch = global.fetch;
    global.fetch = mockFetch as jest.Mock;
    global.URL.createObjectURL = mockCreateObjectUrl;
  });

  afterEach(() => {
    global.fetch = originalFetch;
    global.location.assign = originalLocationAssign;
    global.URL.createObjectURL = originalCreateObjectURL;
    jest.clearAllMocks();
  });

  it("calls fetch with correct url", async () => {
    await downloadSearchResultsCSV(
      new ReadonlyURLSearchParams("status=fake&agency=alsoFake"),
    );
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/search/export?status=fake&agency=alsoFake",
    );
  });

  it("blobs the response", async () => {
    await downloadSearchResultsCSV(
      new ReadonlyURLSearchParams("status=fake&agency=alsoFake"),
    );
    expect(mockBlob).toHaveBeenCalledTimes(1);
  });

  it("sets location with blob result", async () => {
    await downloadSearchResultsCSV(
      new ReadonlyURLSearchParams("status=fake&agency=alsoFake"),
    );
    expect(mockCreateObjectUrl).toHaveBeenCalledWith(getFakeFile());
    expect(mockLocationAssign).toHaveBeenCalledWith("an object url");
  });
});
