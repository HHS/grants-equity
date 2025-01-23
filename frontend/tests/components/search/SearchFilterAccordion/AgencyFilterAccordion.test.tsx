import { act, render, screen } from "@testing-library/react";
import { axe } from "jest-axe";
import { wrapForExpectedError } from "src/utils/testing/commonTestUtils";
import { useTranslationsMock } from "src/utils/testing/intlMocks";

import { ReadonlyURLSearchParams } from "next/navigation";

import { AgencyFilterAccordion } from "src/components/search/SearchFilterAccordion/AgencyFilterAccordion";

jest.mock("next-intl", () => ({
  useTranslations: () => useTranslationsMock(),
}));

jest.mock("src/hooks/useSearchParamUpdater", () => ({
  useSearchParamUpdater: () => ({
    searchParams: new ReadonlyURLSearchParams(),
    updateQueryParams: () => {},
  }),
}));

jest.mock("src/services/globalState/GlobalStateProvider", () => ({
  useGlobalState: () => ({
    setAgencyOptions: () => {},
  }),
}));

jest.mock("react", () => ({
  ...jest.requireActual<typeof import("react")>("react"),
  Suspense: ({ fallback }: { fallback: React.Component }) => fallback,
}));

const fakeOptions = [
  {
    id: "DOC-NIST",
    label: "National Institute of Standards and Technology",
    value: "DOC-NIST",
    children: [
      {
        id: "HI",
        label: "Hello",
        value: "HI",
      },
      {
        id: "There",
        label: "Again",
        value: "There",
      },
    ],
  },
  {
    id: "MOCK-NIST",
    label: "Mational Institute",
    value: "MOCK-NIST",
  },
  {
    id: "MOCK-TRASH",
    label: "Mational TRASH",
    value: "MOCK-TRASH",
    children: [
      {
        id: "TRASH",
        label: "More TRASH",
        value: "TRASH",
      },
    ],
  },
  {
    id: "FAKE",
    label: "Completely fake",
    value: "FAKE",
  },
];

describe("AgencyFilterAccordion", () => {
  it("is accessible (sync)", async () => {
    const { container } = render(
      <AgencyFilterAccordion agencyOptions={fakeOptions} query={new Set()} />,
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it("renders passed prefetched options (non nested)", () => {
    render(
      <AgencyFilterAccordion agencyOptions={fakeOptions} query={new Set()} />,
    );

    expect(screen.getByText("Completely fake")).toBeInTheDocument();
    expect(screen.getByText("Mational TRASH")).toBeInTheDocument();
    expect(screen.getByText("Mational Institute")).toBeInTheDocument();
    expect(
      screen.getByText("National Institute of Standards and Technology"),
    ).toBeInTheDocument();
  });

  it("renders passed prefetched options (nested)", () => {
    const { rerender } = render(
      <AgencyFilterAccordion agencyOptions={fakeOptions} query={new Set()} />,
    );

    const expanderOne = screen.getByText("Mational TRASH");
    const expanderTwo = screen.getByText(
      "National Institute of Standards and Technology",
    );

    act(() => {
      expanderOne.click();
      expanderTwo.click();
    });

    rerender(
      <AgencyFilterAccordion agencyOptions={fakeOptions} query={new Set()} />,
    );
    expect(screen.getByText("More TRASH")).toBeInTheDocument();
    expect(screen.getByText("Hello")).toBeInTheDocument();
    expect(screen.getByText("Again")).toBeInTheDocument();
    expect(
      screen.getByText("National Institute of Standards and Technology"),
    ).toBeInTheDocument();
  });

  // just want to confirm it renders
  it("renders async component if passed a promise (asserting on mock suspended state)", () => {
    render(
      <AgencyFilterAccordion
        agencyOptionsPromise={Promise.resolve(fakeOptions)}
        query={new Set()}
      />,
    );

    expect(screen.getByText("accordion.titles.agency")).toBeInTheDocument();
  });

  it("errors if neither agencyOptions or agencyOptionsPromise are provided", async () => {
    const error = await wrapForExpectedError<Error>(() =>
      render(<AgencyFilterAccordion query={new Set()} />),
    );

    expect(error.message).toEqual(
      "AgencyFilterAccordion must have either agencyOptions or agencyOptionsPromise prop",
    );
  });
});
