import { describe, expect, test } from "vitest";
import { render, within } from "@testing-library/react";
import CenteredContainer from "./CenteredContainer";

describe("Test the CenteredContainer component", () => {
  test("The component is being displayed correctly", () => {
    const { container } = render(
      <CenteredContainer>
        <h1>Hello</h1>
        <p>World</p>
      </CenteredContainer>
    );

    // Get the outermost div tag from the CenteredContainer.
    const outermostDiv = container.querySelector("div");

    // Check if the outermost div tag is defined.
    expect(outermostDiv).toBeDefined();

    // Check if the outermost div tag has only a child (other div tag).
    expect(outermostDiv.childElementCount).toBe(1);

    // Get the innermostDiv div tag from the CenteredContainer.
    const innermostDiv = outermostDiv.querySelector("div");

    // Check if the innermost div tag is defined.
    expect(innermostDiv).toBeDefined();

    // Check if the innermost div tag has only 2 childs.
    expect(innermostDiv.childElementCount).toBe(2);

    // Get the h1 tag in the CenteredContainer component using the text "Hello".
    const title = within(innermostDiv).getByText("Hello");

    // Check if the h1 tag is defined.
    expect(title).toBeDefined();

    // Check if the h1 tag is really a h1 tag.
    expect(title.tagName).toBe("H1");

    // Get the p tag in the CenteredContainer component using the text "World".
    const paragraph = within(innermostDiv).getByText("World");

    // Check if the p tag is defined.
    expect(paragraph).toBeDefined();

    // Check if the p tag is really a p tag.
    expect(paragraph.tagName).toBe("P");
  });
});
