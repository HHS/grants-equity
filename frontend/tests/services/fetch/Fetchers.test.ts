import { EndpointConfig } from "src/services/fetch/endpointConfigs";
import { requesterForEndpoint } from "src/services/fetch/fetchers/fetchers";

const createRequestUrlMock = jest.fn(
  (_method, _basePath, _version, _namespace, subPath: string, _body) => {
    if (subPath) {
      return `fakeurl/${subPath}`;
    }
    return "fakeurl";
  },
);
const fakeJsonBody = {
  data: [],
  errors: [],
  warnings: [],
};

const responseJsonMock = jest.fn().mockResolvedValue(fakeJsonBody);

const fakeResponse = {
  json: responseJsonMock,
  ok: true,
};

const fetchMock = jest.fn().mockResolvedValue(fakeResponse);

const createRequestBodyMock = jest.fn((obj) => JSON.stringify(obj));
const getDefaultHeadersMock = jest.fn(() => ({
  "Content-Type": "application/json",
}));
const throwErrorMock = jest.fn();

jest.mock("src/services/fetch/fetcherHelpers", () => ({
  createRequestUrl: (
    _method: unknown,
    _basePath: unknown,
    _version: unknown,
    _namespace: unknown,
    subPath: string,
    _body: unknown,
  ) =>
    createRequestUrlMock(
      _method,
      _basePath,
      _version,
      _namespace,
      subPath,
      _body,
    ),
  createRequestBody: (arg: unknown) => createRequestBodyMock(arg),
  getDefaultHeaders: () => getDefaultHeadersMock(),
  throwError: (...args: unknown[]): unknown => throwErrorMock(...args),
}));

jest.mock("react", () => ({
  ...jest.requireActual<typeof import("react")>("react"),
  cache: (fn: unknown) => fn,
}));

describe("requesterForEndpoint", () => {
  const basicEndpoint: EndpointConfig = {
    basePath: "hello.org",
    version: "some-strange-version",
    namespace: "sure",
    method: "POST",
  };

  let originalFetch: typeof global.fetch;
  beforeAll(() => {
    originalFetch = global.fetch;
  });
  afterAll(() => {
    global.fetch = originalFetch;
  });
  beforeEach(() => {
    global.fetch = fetchMock;
  });

  it("returns a function", () => {
    expect(typeof requesterForEndpoint(basicEndpoint)).toBe("function");
  });

  it("returns a function that calls `createRequestUrl` and `fetch` with the expected arguments", async () => {
    const requester = requesterForEndpoint(basicEndpoint);
    await requester({
      subPath: "1",
      body: { key: "value" },
      additionalHeaders: { "Header-Name": "headerValue" },
    });
    expect(createRequestUrlMock).toHaveBeenCalledWith(
      "POST",
      "hello.org",
      "some-strange-version",
      "sure",
      "1",
      { key: "value" },
    );
    expect(fetchMock).toHaveBeenCalledWith("fakeurl/1", {
      body: JSON.stringify({ key: "value" }),
      headers: {
        "Content-Type": "application/json",
        "Header-Name": "headerValue",
      },
      method: "POST",
    });
  });
  it("returns a function that returns a fetch response", async () => {
    const requester = requesterForEndpoint(basicEndpoint);
    const response = await requester({
      subPath: "1",
      body: { key: "value" },
      additionalHeaders: { "Header-Name": "headerValue" },
    });
    expect(response).toEqual(fakeResponse);
  });
  it("extracts errors from json response where applicable", async () => {
    fetchMock.mockResolvedValue({
      json: responseJsonMock,
      ok: false,
      status: 404,
      headers: { get: () => "application/json" },
    });

    const requester = requesterForEndpoint(basicEndpoint);

    await requester({
      subPath: "1",
      body: { key: "value" },
      additionalHeaders: { "Header-Name": "headerValue" },
    });
    expect(responseJsonMock).toHaveBeenCalledTimes(1);
    expect(throwErrorMock).toHaveBeenCalledWith(fakeJsonBody, "fakeurl/1");
  });
});
