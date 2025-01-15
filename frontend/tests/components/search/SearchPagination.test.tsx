/* eslint-disable testing-library/no-node-access */
import "@testing-library/jest-dom/extend-expect";

import { render, screen } from "@testing-library/react";
import { axe } from "jest-axe";
import { QueryContext } from "src/app/[locale]/search/QueryProvider";

import React from "react";

import SearchPagination from "src/components/search/SearchPagination";

let fakeTotalPages = "1";
const mockUpdateTotalPages = jest.fn();
const mockUpdateTotalResults = jest.fn();
const mockUpdateQueryParams = jest.fn();

// Mock the useSearchParamUpdater hook
jest.mock("src/hooks/useSearchParamUpdater", () => ({
  useSearchParamUpdater: () => ({
    updateQueryParams: mockUpdateQueryParams,
  }),
}));

const FakeQueryProvider = ({ children }: { children: React.ReactNode }) => {
  const contextValue = {
    updateTotalPages: mockUpdateTotalPages,
    updateTotalResults: mockUpdateTotalResults,
    totalPages: fakeTotalPages,
    queryTerm: "",
    // eslint-disable-next-line
    updateQueryTerm: () => {},
    totalResults: "",
  };
  return (
    <QueryContext.Provider value={contextValue}>
      {children}
    </QueryContext.Provider>
  );
};

beforeEach(() => {
  jest.clearAllMocks();
});

describe("SearchPagination", () => {
  beforeEach(() => {
    fakeTotalPages = "1";
    jest.clearAllMocks();
  });

  it("should not have basic accessibility issues", async () => {
    const { container } = render(
      <FakeQueryProvider>
        <SearchPagination page={1} query={"test"} />
      </FakeQueryProvider>,
    );

    const results = await axe(container, {
      rules: {
        // Disable specific rules that are known to fail due to third-party components
        list: { enabled: false },
        "svg-img-alt": { enabled: false },
      },
    });
    expect(results).toHaveNoViolations();
  });
  it("Renders Pagination component when pages > 0", () => {
    render(
      <FakeQueryProvider>
        <SearchPagination page={1} query={"test"} totalPages={10} />
      </FakeQueryProvider>,
    );

    expect(screen.getByRole("navigation")).toBeInTheDocument();
  });
  it("Does not render Pagination component when pages <= 0", () => {
    fakeTotalPages = "0";
    render(
      <FakeQueryProvider>
        <SearchPagination page={1} query={"test"} totalPages={0} />
      </FakeQueryProvider>,
    );

    expect(screen.queryByRole("navigation")).not.toBeInTheDocument();
  });

  it("renders disabled Pagination component when loading", () => {
    render(
      <FakeQueryProvider>
        <SearchPagination
          page={1}
          query={"test"}
          totalPages={1}
          loading={true}
        />
      </FakeQueryProvider>,
    );

    // some problem with the testing reading the applied styles, so can't figure out
    // how to assert that things are actually disabled here
    expect(screen.queryByRole("navigation")).toHaveAttribute("aria-disabled");
  });

  it("Renders Pagination component when totalResults > 0", () => {
    render(
      <FakeQueryProvider>
        <SearchPagination
          totalResults={"1"}
          page={1}
          query={"test"}
          totalPages={10}
        />
      </FakeQueryProvider>,
    );

    expect(screen.getByRole("navigation")).toBeInTheDocument();
  });
  it("Does not render Pagination component when total results is 0", () => {
    render(
      <FakeQueryProvider>
        <SearchPagination
          page={1}
          query={"test"}
          totalResults={"0"}
          totalPages={0}
        />
      </FakeQueryProvider>,
    );

    expect(screen.queryByRole("navigation")).not.toBeInTheDocument();
  });
  it("updates client state for total pages based on total pages prop", () => {
    const { rerender } = render(
      <FakeQueryProvider>
        <SearchPagination
          page={1}
          query={"test"}
          totalResults={"0"}
          totalPages={11}
        />
      </FakeQueryProvider>,
    );

    expect(mockUpdateTotalPages).toHaveBeenCalledWith("11");
    rerender(
      <FakeQueryProvider>
        <SearchPagination
          page={1}
          query={"test"}
          totalResults={"0"}
          totalPages={12}
        />
      </FakeQueryProvider>,
    );
    expect(mockUpdateTotalPages).toHaveBeenCalledWith("12");
  });

  it("does not update client state for total pages while loading", () => {
    const { rerender } = render(
      <FakeQueryProvider>
        <SearchPagination
          page={1}
          query={"test"}
          totalResults={"0"}
          totalPages={11}
          loading={true}
        />
      </FakeQueryProvider>,
    );

    expect(mockUpdateTotalPages).not.toHaveBeenCalled();
    rerender(
      <FakeQueryProvider>
        <SearchPagination
          page={1}
          query={"test"}
          totalResults={"0"}
          totalPages={12}
          loading={true}
        />
      </FakeQueryProvider>,
    );
    expect(mockUpdateTotalPages).not.toHaveBeenCalled();
  });
  it("updates client state for total results based on total results prop", () => {
    const { rerender } = render(
      <FakeQueryProvider>
        <SearchPagination
          page={1}
          query={"test"}
          totalResults={"11"}
          totalPages={1}
        />
      </FakeQueryProvider>,
    );

    expect(mockUpdateTotalResults).toHaveBeenCalledWith("11");
    rerender(
      <FakeQueryProvider>
        <SearchPagination
          page={1}
          query={"test"}
          totalResults={"12"}
          totalPages={1}
        />
      </FakeQueryProvider>,
    );
    expect(mockUpdateTotalResults).toHaveBeenCalledWith("12");
  });

  it("does not update client state for total results while loading", () => {
    const { rerender } = render(
      <FakeQueryProvider>
        <SearchPagination
          page={1}
          query={"test"}
          totalResults={"11"}
          totalPages={11}
          loading={true}
        />
      </FakeQueryProvider>,
    );

    expect(mockUpdateTotalResults).not.toHaveBeenCalled();
    rerender(
      <FakeQueryProvider>
        <SearchPagination
          page={1}
          query={"test"}
          totalResults={"12"}
          totalPages={12}
          loading={true}
        />
      </FakeQueryProvider>,
    );
    expect(mockUpdateTotalResults).not.toHaveBeenCalled();
  });

  it("updates page state on clicks as expected", () => {
    const { rerender } = render(
      <FakeQueryProvider>
        <SearchPagination
          page={1}
          query={"test"}
          totalResults={"11"}
          totalPages={2}
        />
      </FakeQueryProvider>,
    );
    const pageNumberButton = screen.queryByLabelText("Page 2");
    pageNumberButton?.click();
    expect(mockUpdateQueryParams).toHaveBeenCalledTimes(1);
    expect(mockUpdateQueryParams).toHaveBeenCalledWith(
      "2",
      "page",
      "test",
      false,
    );

    rerender(
      <FakeQueryProvider>
        <SearchPagination
          page={2}
          query={"test"}
          totalResults={"11"}
          totalPages={2}
        />
      </FakeQueryProvider>,
    );
    const previousButton = screen.queryByLabelText("Previous page");
    previousButton?.click();

    expect(mockUpdateQueryParams).toHaveBeenCalledTimes(2);
    expect(mockUpdateQueryParams).toHaveBeenCalledWith(
      "1",
      "page",
      "test",
      false,
    );
  });
});
