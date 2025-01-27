import { createSession, getSession } from "src/services/auth/session";

const getCookiesMock = jest.fn(() => ({
  value: "some cookie value",
}));
const setCookiesMock = jest.fn();
const deleteCookiesMock = jest.fn();

const encodeTextMock = jest.fn((arg: string): string => arg);
const createPublicKeyMock = jest.fn((arg: string): string => arg);

const decryptMock = jest.fn();
const encryptMock = jest.fn();

const cookiesMock = () => {
  return {
    get: getCookiesMock,
    set: setCookiesMock,
    delete: deleteCookiesMock,
  };
};

jest.mock("src/services/auth/sessionUtils", () => ({
  decrypt: (...args: unknown[]) => decryptMock(args) as unknown,
  encrypt: (...args: unknown[]) => encryptMock(args) as unknown,
  CLIENT_JWT_ENCRYPTION_ALGORITHM: "algo one",
  API_JWT_ENCRYPTION_ALGORITHM: "algo two",
  newExpirationDate: () => new Date(0),
}));

jest.mock("next/headers", () => ({
  cookies: () => cookiesMock(),
}));

jest.mock("src/constants/environments", () => ({
  environment: {
    SESSION_SECRET: "session secret",
    API_JWT_PUBLIC_KEY: "api secret",
  },
}));

jest.mock("src/utils/generalUtils", () => ({
  encodeText: (arg: string): string => encodeTextMock(arg),
}));

jest.mock("crypto", () => ({
  createPublicKey: (arg: string): string => createPublicKeyMock(arg),
}));

describe("getSession", () => {
  afterEach(() => jest.clearAllMocks());
  it("initializes session secrets if necessary", async () => {
    await getSession();
    expect(encodeTextMock).toHaveBeenCalledWith("session secret");
    expect(createPublicKeyMock).toHaveBeenCalledWith("api secret");
  });
  it("calls decrypt with the correct arguments and returns successfully", async () => {
    decryptMock.mockReturnValue({
      token: "some decrypted token",
      exp: 123,
    });
    const session = await getSession();
    expect(decryptMock).toHaveBeenCalledTimes(2);
    expect(decryptMock).toHaveBeenCalledWith([
      "some cookie value",
      "session secret",
      "algo one",
    ]);
    expect(decryptMock).toHaveBeenCalledWith([
      "some decrypted token",
      "api secret",
      "algo two",
    ]);
    expect(session).toEqual({
      token: "some decrypted token",
      exp: 123,
    });
  });
  it("returns null if client token decrypt does not return a payload and token", async () => {
    decryptMock.mockReturnValue(null);
    const session = await getSession();
    expect(session).toEqual(null);
  });
  it("returns null if api token decrypt does not return a payload", async () => {
    decryptMock
      .mockReturnValueOnce({
        token: "some decrypted token",
        exp: 123,
      })
      .mockReturnValueOnce(null);
    const session = await getSession();
    expect(session).toEqual(null);
  });
});

describe("createSession", () => {
  afterEach(() => jest.clearAllMocks());
  // to get this to work we'd need to manage resetting all modules before the test, which is a bit of a pain
  // eslint-disable-next-line jest/no-disabled-tests
  it.skip("initializes session secrets if necessary", async () => {
    await createSession("nothingSpecial");
    expect(encodeTextMock).toHaveBeenCalledWith("session secret");
    expect(createPublicKeyMock).toHaveBeenCalledWith("api secret");
  });
  it("calls cookie.set with expected values", async () => {
    encryptMock.mockReturnValue("encrypted session");
    await createSession("nothingSpecial");
    expect(encryptMock).toHaveBeenCalledWith([
      "nothingSpecial",
      new Date(0),
      "session secret",
    ]);
    expect(setCookiesMock).toHaveBeenCalledTimes(1);
    expect(setCookiesMock).toHaveBeenCalledWith(
      "session",
      "encrypted session",
      {
        httpOnly: true,
        secure: false, // true only in prod for now
        expires: new Date(0),
        sameSite: "lax",
        path: "/",
      },
    );
  });
});
