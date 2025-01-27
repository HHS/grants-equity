import { render, screen } from "@testing-library/react";
import { identity } from "lodash";
import Search from "src/app/[locale]/search/page";
import { SEARCH_NO_STATUS_VALUE } from "src/constants/search";
import { useTranslationsMock } from "src/utils/testing/intlMocks";

import { ReadonlyURLSearchParams } from "next/navigation";

// test without feature flag functionality
jest.mock("src/hoc/withFeatureFlag", () =>
  jest.fn((Component: React.Component) => Component),
);

jest.mock("next-intl/server", () => ({
  getTranslations: () => identity,
  setRequestLocale: identity,
}));

jest.mock("next-intl", () => ({
  useTranslations: () => useTranslationsMock(),
}));

jest.mock("src/hooks/useSearchParamUpdater", () => ({
  useSearchParamUpdater: () => ({
    searchParams: new ReadonlyURLSearchParams(),
  }),
}));

// // currently, with Suspense mocked out below to always show fallback content,
// // the components making the fetch calls are never being rendered so we do not need to mock them out
// // uncomment this if we figure out a way to properly test the underlying async components
// jest.mock("src/services/fetch/fetchers", () => ({
//   get searchOpportunityFetcher() {
//     return new MockSearchOpportunityAPI();
//   },
// }));

jest.mock("next/navigation", () => ({
  ...jest.requireActual<typeof import("next/navigation")>("next/navigation"),
  useRouter: () => ({
    // eslint-disable-next-line @typescript-eslint/no-empty-function
    push: () => {},
  }),
}));

/*
  nested async server components (< ...Fetcher />) are currently breaking the render.
  stated workarounds are not working. to get testing minimally working, overriding
  Suspense to force display of fallback UI.

  for more see https://github.com/testing-library/react-testing-library/issues/1209
// */
jest.mock("react", () => ({
  ...jest.requireActual<typeof import("react")>("react"),
  Suspense: ({ fallback }: { fallback: React.Component }) => fallback,
  cache: (fn: unknown) => fn,
  use: jest.fn((e: { [key: string]: string }) => e),
}));

const fetchMock = jest.fn().mockResolvedValue({
  json: jest.fn().mockResolvedValue({ data: [], errors: [], warnings: [] }),
  ok: true,
  status: 200,
});

// working around the complexities of exporting the component wrapped in a feature flag
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const TypedSearchPageComponent = Search as (props: any) => React.JSX.Element;

describe("Search Route", () => {
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
  it("renders the search page with expected checkboxes checked", async () => {
    const mockSearchParams = {
      status: "forecasted,posted",
    };

    render(
      TypedSearchPageComponent({
        searchParams: mockSearchParams,
        params: { locale: "en" },
      }),
    );

    // translation service is mocked, so the expected label here is the translation key rather than the label text
    const forecastedCheckbox = await screen.findByLabelText(
      "opportunityStatus.label.forecasted",
    );
    expect(forecastedCheckbox).toBeInTheDocument();
    expect(forecastedCheckbox).toBeChecked();

    const postedCheckbox = await screen.findByLabelText(
      "opportunityStatus.label.posted",
    );
    expect(postedCheckbox).toBeInTheDocument();
    expect(postedCheckbox).toBeChecked();

    const closedCheckbox = await screen.findByLabelText(
      "opportunityStatus.label.closed",
    );
    expect(closedCheckbox).toBeInTheDocument();
    expect(closedCheckbox).not.toBeChecked();

    const archivedCheckbox = await screen.findByLabelText(
      "opportunityStatus.label.archived",
    );
    expect(archivedCheckbox).toBeInTheDocument();
    expect(archivedCheckbox).not.toBeChecked();
  });

  it("renders the search page with all opportunities if no status selected", async () => {
    const mockSearchParams = {
      status: SEARCH_NO_STATUS_VALUE,
    };
    render(
      TypedSearchPageComponent({
        searchParams: mockSearchParams,
        params: { locale: "en" },
      }),
    );

    // None should be checked if the "no status checked" value is present.
    const statuses = ["forecasted", "posted", "closed", "archived"];
    for (const status of statuses) {
      const checkbox = await screen.findByLabelText(
        `opportunityStatus.label.${status}`,
      );
      expect(checkbox).toBeInTheDocument();
      expect(checkbox).not.toBeChecked();
    }
  });

  it("renders the search page two status by default", async () => {
    const mockSearchParams = {
      status: undefined,
    };
    render(
      TypedSearchPageComponent({
        searchParams: mockSearchParams,
        params: { locale: "en" },
      }),
    );

    // These should be clicked if no status is present.
    const clicked = ["forecasted", "posted"];
    for (const status of clicked) {
      const checkbox = await screen.findByLabelText(
        `opportunityStatus.label.${status}`,
      );
      expect(checkbox).toBeInTheDocument();
      expect(checkbox).toBeChecked();
    }

    // These should not be clicked if no status is present.
    const noClicked = ["closed", "archived"];
    for (const status of noClicked) {
      const checkbox = await screen.findByLabelText(
        `opportunityStatus.label.${status}`,
      );
      expect(checkbox).toBeInTheDocument();
      expect(checkbox).not.toBeChecked();
    }
  });
});
