import { render, screen, waitFor } from "@testing-library/react";
import { axe } from "jest-axe";
import { identity } from "lodash";
import Maintenance from "src/app/[locale]/maintenance/page";
import {
  localeParams,
  mockMessages,
  useTranslationsMock,
} from "src/utils/testing/intlMocks";

jest.mock("next-intl/server", () => ({
  getTranslations: () => identity,
  setRequestLocale: identity,
}));

jest.mock("next-intl", () => ({
  useTranslations: () => useTranslationsMock(),
  useMessages: () => mockMessages,
}));

describe("Maintenance", () => {
  it("renders intro text", () => {
    render(<Maintenance params={localeParams} />);

    const content = screen.getByText("heading");

    expect(content).toBeInTheDocument();
  });

  it("passes accessibility scan", async () => {
    const { container } = render(<Maintenance params={localeParams} />);
    const results = await waitFor(() => axe(container));

    expect(results).toHaveNoViolations();
  });
});
