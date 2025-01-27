import { act, renderHook } from "@testing-library/react";
import {
  GlobalStateProvider,
  useGlobalState,
} from "src/services/globalState/GlobalStateProvider";

import { ReactNode } from "react";

const wrapper = ({ children }: { children: ReactNode }) => (
  <GlobalStateProvider>{children}</GlobalStateProvider>
);

describe("useGlobalState", () => {
  afterEach(() => {
    jest.resetAllMocks();
  });
  test("returns default global state", () => {
    const { result } = renderHook(() => useGlobalState((state) => state), {
      wrapper,
    });

    const { agencyOptions } = result.current;

    expect(agencyOptions).toEqual([]);
  });
  test("allows updating global state", () => {
    const { result, rerender } = renderHook(
      () => useGlobalState((state) => state),
      { wrapper },
    );

    const { setAgencyOptions } = result.current;

    act(() => {
      setAgencyOptions([
        {
          id: "MOCK-NIST",
          label: "Mational Institute",
          value: "MOCK-NIST",
        },
      ]);
    });

    rerender();

    const { agencyOptions } = result.current;
    expect(agencyOptions).toEqual([
      {
        id: "MOCK-NIST",
        label: "Mational Institute",
        value: "MOCK-NIST",
      },
    ]);
  });
});
