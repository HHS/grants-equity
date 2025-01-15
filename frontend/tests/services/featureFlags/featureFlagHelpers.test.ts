import {
  FEATURE_FLAGS_KEY,
  getFeatureFlagsFromCookie,
  isValidFeatureFlag,
  parseFeatureFlagsFromString,
  setCookie,
} from "src/services/featureFlags/featureFlagHelpers";

import {
  RequestCookies,
  ResponseCookies,
} from "next/dist/compiled/@edge-runtime/cookies";
import { NextRequest } from "next/server";

jest.mock("src/constants/defaultFeatureFlags", () => ({
  defaultFeatureFlags: {
    feature1: true,
    feature2: false,
    feature3: true,
  },
}));

const COOKIE_VALUE: { [key: string]: boolean } = { feature1: true };

const mockSetCookies = jest.fn();

function MockRequestCookiesModule(cookieValue = COOKIE_VALUE) {
  return {
    get: (name: string) => {
      if (name === FEATURE_FLAGS_KEY) {
        return {
          value: JSON.stringify(cookieValue),
        };
      }
    },
    set: mockSetCookies,
  } as object as NextRequest["cookies"];
}

function MockResponseCookiesModule(cookieValue = COOKIE_VALUE) {
  return {
    get: (name: string) => {
      if (name === FEATURE_FLAGS_KEY) {
        return {
          value: JSON.stringify(cookieValue),
        };
      }
    },
    set: mockSetCookies,
  } as object as ResponseCookies;
}

describe("getFeatureFlagsFromCookie", () => {
  test('getter loads feature flags with server-side NextRequest["cookies"]', () => {
    expect(getFeatureFlagsFromCookie(MockRequestCookiesModule())).toEqual(
      COOKIE_VALUE,
    );
  });

  // // do we still need to support this?
  // eslint-disable-next-line jest/no-disabled-tests, jest/no-commented-out-tests
  // test("getter loads feature flags with server-side getServerSideProps cookies", () => {
  //   const cookieRecord = {
  //     // Was unable to override flag keys. Use feature flag class invocation default for now.
  //     _ff: JSON.stringify(COOKIE_VALUE),
  //   };
  //   expect(getFeatureFlagsFromCookie(cookieRecord)).toEqual(COOKIE_VALUE);
  // });

  test("does not error if the cookie value is empty", () => {
    expect(
      getFeatureFlagsFromCookie(new RequestCookies(new Headers())),
    ).toEqual({});
  });

  test("does not error if the cookie value is invalid", () => {
    const invalidCookieValue = "----------------";
    expect(
      getFeatureFlagsFromCookie(
        new RequestCookies(
          new Headers({ Cookie: `${FEATURE_FLAGS_KEY}=${invalidCookieValue}` }),
        ),
      ),
    ).toEqual({});
  });

  test("does not include invalid feature flags even if included in cookie value", () => {
    const invalidFeatureFlag = "someInvalidFeatureFlagName";
    expect(
      getFeatureFlagsFromCookie(
        new RequestCookies(
          new Headers({
            Cookie: `${FEATURE_FLAGS_KEY}=${invalidFeatureFlag}:true`,
          }),
        ),
      ),
    ).toEqual({});
  });

  test("does not include feature flags if the value is not a boolean", () => {
    const validFeatureFlag = "feature1";
    expect(
      getFeatureFlagsFromCookie(
        new RequestCookies(
          new Headers({
            Cookie: `${FEATURE_FLAGS_KEY}=${validFeatureFlag}:someInvalidFeatureFlagValue"`,
          }),
        ),
      ),
    ).toEqual({});
  });

  test.each(["string", '"string"', 1, 1.1, "true", ""])(
    "does not include feature flags if the value is not a boolean like %p",
    (featureFlagValue) => {
      const featureName = "feature1";
      expect(
        getFeatureFlagsFromCookie(
          new RequestCookies(
            new Headers({
              Cookie: `${FEATURE_FLAGS_KEY}=${featureName}:${featureFlagValue}`,
            }),
          ),
        ),
      ).toEqual({});
    },
  );
});

describe("isValidFeatureFlag", () => {
  test("correctly identifies valid feature flag names", () => {
    Object.keys({
      feature1: true,
      feature2: false,
      feature3: true,
    }).forEach((name) => {
      expect(isValidFeatureFlag(name)).toEqual(true);
    });
    const invalidFeatureFlagName = "someInvalidFeatureFlag--------------";
    expect(isValidFeatureFlag(invalidFeatureFlagName)).toEqual(false);
  });
});

describe("parseFeatureFlagsFromString", () => {
  test("correctly parses a valid query param string", () => {
    const expectedFeatureFlags = {
      feature1: false,
      feature2: true,
    };
    const validQueryParamString = "feature1:false;feature2:true";
    expect(parseFeatureFlagsFromString(validQueryParamString)).toEqual(
      expectedFeatureFlags,
    );
    const validQueryParamStringWithExtraCharacters =
      ";feature1: false; feature2 : true ;";
    expect(
      parseFeatureFlagsFromString(validQueryParamStringWithExtraCharacters),
    ).toEqual(expectedFeatureFlags);
  });

  test("returns {} if null param", () => {
    expect(parseFeatureFlagsFromString(null)).toEqual({});
  });

  test("returns {} if empty string param", () => {
    expect(parseFeatureFlagsFromString("")).toEqual({});
  });

  test.each([
    "sadfkdfj",
    ";;;;;;;;;;;;;",
    "truetruetrue=false",
    "true=false",
    "!@#$%^&*(){}[]:\";|'<.,./?\\`~",
  ])("gracefully handles garbled values like %s", (queryParamString) => {
    const featureFlags = parseFeatureFlagsFromString(queryParamString);
    expect(featureFlags).toEqual({});
  });

  test.each([
    ["feature1", "true", true],
    ["invalidFeatureFlag", "true", false],
    ["feature1", "invalidFlagValue", false],
  ])(
    "omits invalid flag names and values (case %#)",
    (flagName, flagValue, isValid) => {
      const queryParamString = `${flagName}:${flagValue}`;
      const featureFlags = parseFeatureFlagsFromString(queryParamString);
      expect(Object.keys(featureFlags).includes(flagName)).toBe(isValid);
    },
  );
});

describe("setCookie", () => {
  test("calls cookie set method with proper arguments", () => {
    setCookie('{"anyFeatureFlagName":"anyValue"}', MockResponseCookiesModule());
    expect(mockSetCookies).toHaveBeenCalledWith({
      name: FEATURE_FLAGS_KEY,
      value: '{"anyFeatureFlagName":"anyValue"}',
      expires: expect.any(Date) as Date,
    });
  });
});
