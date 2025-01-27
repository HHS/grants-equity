/**
 * @jest-environment ./src/utils/testing/jsdomNodeEnvironment.ts
 */

import { fireEvent, render, screen } from "@testing-library/react";
import FeatureFlags from "src/app/[locale]/dev/feature-flags/page";

const MOCK_DEFAULT_FEATURE_FLAGS = {
  someFakeFeature1: true,
  someFakeFeature2: true,
  someFakeFeature3: true,
};

type MockFeatureFlagKeys = keyof typeof MOCK_DEFAULT_FEATURE_FLAGS;

const mockUseFeatureFlags = jest.fn(() => ({
  featureFlags: MOCK_DEFAULT_FEATURE_FLAGS,
  setFeatureFlag: (flagName: MockFeatureFlagKeys, value: boolean) =>
    mockSetFeatureFlag(flagName, value),
}));

const mockSetFeatureFlag = jest.fn(
  (flagName: MockFeatureFlagKeys, value: boolean) => {
    MOCK_DEFAULT_FEATURE_FLAGS[flagName] = value;
  },
);

jest.mock("react", () => ({
  ...jest.requireActual<typeof import("react")>("react"),
  use: jest.fn(() => ({
    locale: "en",
  })),
}));

jest.mock("src/hooks/useFeatureFlags", () => ({
  useFeatureFlags: () => mockUseFeatureFlags(),
}));

describe("Feature flags page", () => {
  it("should render all feature flags", () => {
    render(<FeatureFlags />);
    expect(mockUseFeatureFlags).toHaveBeenCalled();
    Object.keys(MOCK_DEFAULT_FEATURE_FLAGS).forEach((name) => {
      expect(screen.getByText(name)).toBeInTheDocument();
      expect(screen.getByTestId(`${name}-status`)).toHaveTextContent("Enabled");
    });
  });

  it("clicking on a feature flag enable and disable buttons should update state", () => {
    const { rerender } = render(<FeatureFlags />);
    Object.keys(MOCK_DEFAULT_FEATURE_FLAGS).forEach((name) => {
      const enableButton = screen.getByTestId(`enable-${name}`);
      const disableButton = screen.getByTestId(`disable-${name}`);
      const statusElement = screen.getByTestId(`${name}-status`);

      expect(statusElement).toHaveTextContent("Enabled");
      fireEvent.click(enableButton);
      rerender(<FeatureFlags />);
      expect(statusElement).toHaveTextContent("Enabled");

      fireEvent.click(disableButton);
      rerender(<FeatureFlags />);
      expect(statusElement).toHaveTextContent("Disabled");

      fireEvent.click(disableButton);
      rerender(<FeatureFlags />);
      expect(statusElement).toHaveTextContent("Disabled");

      fireEvent.click(enableButton);
      rerender(<FeatureFlags />);
      expect(statusElement).toHaveTextContent("Enabled");
    });
  });
});
