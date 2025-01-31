/**
 * @file Service for checking and managing feature flags
 */

import {
  defaultFeatureFlags,
  FeatureFlags,
} from "src/constants/defaultFeatureFlags";
import { featureFlags } from "src/constants/environments";
import {
  FEATURE_FLAGS_KEY,
  getFeatureFlagsFromCookie,
  isValidFeatureFlag,
  parseFeatureFlagsFromString,
  setCookie,
} from "src/services/featureFlags/featureFlagHelpers";
import { OptionalStringDict } from "src/types/searchRequestURLTypes";

import { ReadonlyRequestCookies } from "next/dist/server/web/spec-extension/adapters/request-cookies";
import { NextRequest, NextResponse } from "next/server";

/**
 * Class for reading and managing feature flags on the server.
 *
 * Holds default and env var based values in class, and exposes two functions:
 *
 * - middleware: for use in setting feature flags on cookies in next middleware
 * - isFeatureEnabled: for checking if a feature is currently enabled, requires
 * passing in existing request cookies
 *
 */
export class FeatureFlagsManager {
  // Define all feature flags here! You can override these in your
  // browser, once a default is defined here.
  private _defaultFeatureFlags = defaultFeatureFlags;

  // pass in env var values at instantiation, as these won't change during runtime
  // this supports easier integration of the class on the client side, as server side flags can be passed down
  private _envVarFlags;

  constructor(envVarFlags: FeatureFlags) {
    this._envVarFlags = envVarFlags;
  }

  get defaultFeatureFlags(): FeatureFlags {
    return { ...this._defaultFeatureFlags };
  }

  private get featureFlagsFromEnvironment(): FeatureFlags {
    return { ...this._envVarFlags };
  }

  /*

 * - Flags set by environment variables are the first override to default values
    - Flags set in the /dev/feature-flags admin view will be set in the cookie
    - Flags set in query params will result in the flag value being stored in the cookie
    - As query param values are set in middleware on each request, query params have the highest precedence


  */
  get featureFlags(): FeatureFlags {
    return {
      ...this.defaultFeatureFlags,
      ...this.featureFlagsFromEnvironment,
    };
  }

  /**
   * Check whether a feature flag is enabled
   *
   * @description  Server side flag values are interpreted as follows:
   *
   * - Default values and any environment variable overrides are grabbed from the class
   * - Any flags from the passed in request cookie will override the class's stored flags
   * - Any flags set in the query param are a final override, though these likely will have already been set on the cookie
   * by the middleware
   *
   * @param name - Feature flag name
   * @param cookies - server side cookies to check for enabled flags
   * @param searchParams - search params to check for enabled flags
   * @example isFeatureEnabled("featureFlagName")
   */
  isFeatureEnabled(
    name: string,
    cookies: NextRequest["cookies"] | ReadonlyRequestCookies,
    searchParams?: OptionalStringDict,
  ): boolean {
    if (!isValidFeatureFlag(name)) {
      throw new Error(`\`${name}\` is not a valid feature flag`);
    }

    // Start with the default feature flag setting
    const currentFeatureFlags = {
      ...this.featureFlags,
      ...getFeatureFlagsFromCookie(cookies),
    };
    let featureFlagBoolean = currentFeatureFlags[name];

    // Query params take precedent. Override the returned value if we see them
    if (searchParams && searchParams[FEATURE_FLAGS_KEY]) {
      const featureFlagsObject = parseFeatureFlagsFromString(searchParams._ff);
      featureFlagBoolean = featureFlagsObject[name];
    }

    return featureFlagBoolean;
  }

  /**
   * Load feature flags from class, existing cookie, and query params and set them on the response cookie. This allows for
   * feature flags to be set via url query params as well.
   *
   * Expects a query string with a param of `_ff`. For example, `example.com?_ff=showSite:true;enableClaimFlow:false`
   * would enable `showSite` and disable `enableClaimFlow`.
   *
   * Note that since flags set in a query param are persisted into the cookie,  simply removing a query param from a url
   * will not revert the feature flag value to the value specified in environment variable or default.
   * To reset a flag value you'll need to clear cookies or open a new private browser
   *
   * This functionality allows environment variable based feature flag values, which otherwise cannot be made
   * available to the client in our current setup, to be exposed to the client via the cookie.
   *
   */
  middleware(request: NextRequest, response: NextResponse): NextResponse {
    const paramValue = request.nextUrl.searchParams.get(FEATURE_FLAGS_KEY);

    const featureFlagsFromQuery =
      paramValue === "reset"
        ? this.featureFlags
        : parseFeatureFlagsFromString(paramValue);

    // previously there was logic here to return early if there were no feature flags active
    // beyond default values. Unfortunately, this breaks the implementation of the feature
    // flag admin view, which depends on reading all flags from cookies, so the logic has beeen removed

    const featureFlags = {
      ...this.featureFlags,
      ...getFeatureFlagsFromCookie(request.cookies),
      ...featureFlagsFromQuery,
    };

    setCookie(JSON.stringify(featureFlags), response.cookies);

    return response;
  }
}

export const featureFlagsManager = new FeatureFlagsManager(featureFlags);
