import { render, screen } from "@testing-library/react";
import { identity } from "lodash";
import UserDisplay from "src/app/[locale]/user/page";
import { localeParams } from "src/utils/testing/intlMocks";

jest.mock("next-intl/server", () => ({
  getTranslations: () => identity,
}));

jest.mock("next/navigation", () => ({
  useRouter: () => ({
    push: () => null,
  }),
}));

const searchParams = (query: { [key: string]: string }) =>
  new Promise<{ [key: string]: string }>((resolve) => {
    resolve(query);
  });

describe("User Page", () => {
  test("It renders", async () => {
    const component = await UserDisplay({
      params: localeParams,
      searchParams: searchParams({ message: "success" }),
    });
    render(component);
    expect(screen.getByText(/success/i)).toBeInTheDocument();
  });
});
