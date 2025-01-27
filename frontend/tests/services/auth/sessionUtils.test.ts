import {
  decrypt,
  deleteSession,
  encrypt,
} from "src/services/auth/sessionUtils";

type RecursiveObject = {
  [key: string]: () => RecursiveObject | string;
};

const getCookiesMock = jest.fn();
const setCookiesMock = jest.fn();
const deleteCookiesMock = jest.fn();
const reallyFakeMockJWTConstructor = jest.fn();
const setProtectedHeaderMock = jest.fn(() => fakeJWTInstance());
const setIssuedAtMock = jest.fn(() => fakeJWTInstance());
const setExpirationTimeMock = jest.fn(() => fakeJWTInstance());
const signMock = jest.fn();
const jwtVerifyMock = jest.fn();

const fakeKey = new Uint8Array([1, 2, 3]);

// close over the token
// all of this rigmarole means that the mocked signing functionality will output the token passed into it
const setJWTMocksWithToken = (token: string) => {
  signMock.mockImplementation(() => token);
};

const fakeJWTInstance = (): RecursiveObject => ({
  setProtectedHeader: setProtectedHeaderMock,
  setIssuedAt: setIssuedAtMock,
  setExpirationTime: setExpirationTimeMock,
  sign: signMock,
});

const cookiesMock = () => {
  return {
    get: getCookiesMock,
    set: setCookiesMock,
    delete: deleteCookiesMock,
  };
};

jest.mock("next/headers", () => ({
  cookies: () => cookiesMock(),
}));

jest.mock("jose", () => ({
  jwtVerify: (...args: unknown[]): unknown => jwtVerifyMock(...args),
  SignJWT: function SignJWTMock(
    this: {
      setProtectedHeader: typeof jest.fn;
      setIssuedAt: typeof jest.fn;
      setExpirationTime: typeof jest.fn;
      sign: typeof jest.fn;
      token: string;
    },
    { token = "" } = {},
  ) {
    reallyFakeMockJWTConstructor();
    setJWTMocksWithToken(token);
    return {
      ...fakeJWTInstance(),
    };
  },
}));

describe("deleteSession", () => {
  afterEach(() => jest.clearAllMocks());
  it("calls cookie.delete with expected values", async () => {
    await deleteSession();
    expect(deleteCookiesMock).toHaveBeenCalledTimes(1);
    expect(deleteCookiesMock).toHaveBeenCalledWith("session");
  });
});

describe("encrypt", () => {
  afterEach(() => jest.clearAllMocks());
  it("calls all the JWT functions with expected values and returns expected value", async () => {
    const token = "fakeToken";
    const expiresAt = new Date();

    const encrypted = await encrypt(token, expiresAt, fakeKey);

    expect(reallyFakeMockJWTConstructor).toHaveBeenCalledTimes(1);

    expect(setProtectedHeaderMock).toHaveBeenCalledTimes(1);
    expect(setProtectedHeaderMock).toHaveBeenCalledWith({ alg: "HS256" });

    expect(setIssuedAtMock).toHaveBeenCalledTimes(1);

    expect(setExpirationTimeMock).toHaveBeenCalledTimes(1);
    expect(setExpirationTimeMock).toHaveBeenCalledWith(expiresAt);

    expect(signMock).toHaveBeenCalledTimes(1);
    expect(signMock).toHaveBeenCalledWith(fakeKey);

    // this is synthetic but generally proves things are working
    expect(encrypted).toEqual(token);
  });
});

describe("decrypt", () => {
  const cookie = "fakeCookie";
  afterEach(() => jest.clearAllMocks());
  it("calls JWT verification with expected values and returns payload", async () => {
    jwtVerifyMock.mockImplementation((...args) => ({ payload: args }));
    const decrypted = await decrypt(cookie, fakeKey, "HS256");

    expect(jwtVerifyMock).toHaveBeenCalledTimes(1);
    expect(jwtVerifyMock).toHaveBeenCalledWith(cookie, fakeKey, {
      algorithms: ["HS256"],
    });

    expect(decrypted).toEqual([cookie, fakeKey, { algorithms: ["HS256"] }]);
  });

  it("returns null on error", async () => {
    jwtVerifyMock.mockImplementation(() => {
      throw new Error();
    });
    const decrypted = await decrypt(cookie, fakeKey, "HS256");
    expect(decrypted).toEqual(null);
  });
});
