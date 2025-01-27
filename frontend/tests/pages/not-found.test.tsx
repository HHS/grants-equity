import { render, screen, waitFor } from "@testing-library/react";
import { axe } from "jest-axe";
import { identity } from "lodash";
import PageNotFound from "src/app/[locale]/not-found";
import { useTranslationsMock } from "src/utils/testing/intlMocks";

jest.mock("react", () => ({
  ...jest.requireActual<typeof import("react")>("react"),
  use: jest.fn(() => ({
    locale: "en",
  })),
}));

jest.mock("next-intl/server", () => ({
  getTranslations: () => identity,
  unstable_setRequestLocale: identity,
}));

jest.mock("next-intl", () => ({
  useTranslations: () => useTranslationsMock(),
}));

describe("PageNotFound", () => {
  it("renders alert with grants.gov link", () => {
    render(<PageNotFound />);

    const alert = screen.queryByTestId("alert");

    expect(alert).toBeInTheDocument();
  });

  it("links back to the home page", () => {
    render(<PageNotFound />);
    const link = screen.getByRole("link", { name: "visit_homepage_button" });

    expect(link).toBeInTheDocument();
  });

  it("passes accessibility scan", async () => {
    const { container } = render(<PageNotFound />);
    const results = await waitFor(() => axe(container));

    expect(results).toHaveNoViolations();
  });
});
