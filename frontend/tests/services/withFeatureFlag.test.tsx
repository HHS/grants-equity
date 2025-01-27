import Cookies from "js-cookie";
import { identity } from "lodash";
import withFeatureFlag from "src/hoc/withFeatureFlag";
import { render } from "tests/react-utils";

let enableFeature = false;

jest.mock("src/services/featureFlags/FeatureFlagManager", () => {
  class FakeFeatureFlagManager {
    isFeatureEnabled() {
      return enableFeature;
    }
  }

  return {
    featureFlagsManager: new FakeFeatureFlagManager(),
  };
});

jest.mock("next/headers", () => ({
  cookies: () => Cookies,
}));

const searchPromise = (query: { [key: string]: string }) =>
  new Promise<{ [key: string]: string }>((resolve) => {
    resolve(query);
  });

describe("WithFeatureFlag", () => {
  afterEach(() => {
    enableFeature = false;
  });
  afterAll(() => {
    jest.restoreAllMocks();
  });
  it("adds search params as prop to wrapped component", async () => {
    const OriginalComponent = jest.fn();
    const searchParams = { any: "param" };
    const WrappedComponent = withFeatureFlag(
      OriginalComponent,
      "searchOff",
      identity,
    );
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    const component = await WrappedComponent({
      searchParams: searchPromise(searchParams),
    });
    // eslint-disable-next-line @typescript-eslint/no-unsafe-argument
    render(component);
    expect(OriginalComponent).toHaveBeenCalledTimes(1);
    expect(OriginalComponent).toHaveBeenCalledWith(
      { searchParams: searchPromise(searchParams) },
      undefined,
    );
  });
  it("calls onEnabled during wrapped component render when feature flag is enabled", async () => {
    enableFeature = true;
    const OriginalComponent = jest.fn();
    const onEnabled = jest.fn();
    const searchParams = { any: "param" };
    const WrappedComponent = withFeatureFlag(
      OriginalComponent,
      "searchOff",
      onEnabled,
    );
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    const component = await WrappedComponent({
      searchParams: searchPromise(searchParams),
    });
    // eslint-disable-next-line @typescript-eslint/no-unsafe-argument
    render(component);
    expect(onEnabled).toHaveBeenCalledTimes(1);
  });
});
