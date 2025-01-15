import { act, render, screen, waitFor } from "@testing-library/react";
import { Breakpoints } from "src/types/uiTypes";

import ContentDisplayToggle from "src/components/ContentDisplayToggle";

describe("ContentDisplayToggle", () => {
  it("Renders without errors", () => {
    render(
      <ContentDisplayToggle
        showCallToAction="show me content"
        hideCallToAction="do not show me content"
      >
        <div>Some content</div>
      </ContentDisplayToggle>,
    );
    const component = screen.getByTestId("content-display-toggle");
    expect(component).toBeInTheDocument();
  });

  it("Renders children with default state true", () => {
    render(
      <ContentDisplayToggle
        showCallToAction="show me content"
        hideCallToAction="do not show me content"
        showContentByDefault={true}
      >
        <div>Some content</div>
      </ContentDisplayToggle>,
    );
    const childContent = screen.getByTestId("toggled-content-container");
    expect(childContent).not.toHaveClass("display-none");
  });

  it("Does not render children with default state false", () => {
    render(
      <ContentDisplayToggle
        showCallToAction="show me content"
        hideCallToAction="do not show me content"
        showContentByDefault={false}
      >
        <div>Some content</div>
      </ContentDisplayToggle>,
    );

    const childContent = screen.getByTestId("toggled-content-container");
    expect(childContent).toHaveClass("display-none");
  });

  it("Toggles content display on button click", async () => {
    render(
      <ContentDisplayToggle
        showCallToAction="show me content"
        hideCallToAction="do not show me content"
        showContentByDefault={false}
      >
        <div>Some content</div>
      </ContentDisplayToggle>,
    );
    const childContent = screen.getByTestId("toggled-content-container");
    expect(childContent).toHaveClass("display-none");

    const toggleButton = screen.getByText("show me content");
    expect(toggleButton).toBeInTheDocument();
    act(() => {
      toggleButton.click();
    });

    await waitFor(() => {
      expect(childContent).not.toHaveClass("display-none");
    });
  });

  // this test is basically useless, as it is only asserting that classes are being applied
  // all of these tests are not great, but it seems that uswds styling is not being loaded by
  // testing library / jsdom, so the ability to test based on actual user facing visibility is heavily limited
  // eslint-disable-next-line jest/no-disabled-tests
  it.skip("Toggles responds by hiding button and displaying content above passed breakpoint", () => {
    render(
      <ContentDisplayToggle
        showCallToAction="show me content"
        hideCallToAction="do not show me content"
        showContentByDefault={false}
        breakpoint={Breakpoints.TABLET}
      >
        <div>Some content</div>
      </ContentDisplayToggle>,
    );
    const childContent = screen.getByTestId("toggled-content-container");
    expect(childContent).toHaveClass("tablet:display-block");

    const toggleButton = screen.getByTestId("content-display-toggle");
    expect(toggleButton).toHaveClass("tablet:display-none");
  });
});
