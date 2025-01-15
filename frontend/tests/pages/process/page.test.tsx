import { render, screen, waitFor } from "@testing-library/react";
import { axe } from "jest-axe";
import { identity } from "lodash";
import Process from "src/app/[locale]/process/page";
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

describe("Process", () => {
  it("renders intro text", () => {
    render(Process({ params: localeParams }));

    const content = screen.getByText("intro.content");

    expect(content).toBeInTheDocument();
  });

  it("passes accessibility scan", async () => {
    const { container } = render(Process({ params: localeParams }));
    const results = await waitFor(() => axe(container));

    expect(results).toHaveNoViolations();
  });
});
