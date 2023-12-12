import { describe, expect, test } from "vitest";
import { render, within } from "@testing-library/react";
import BackgroundContainer from "./BackgroundContainer";

describe("Test the BackgroundContainer component", () => {
  test("The component is being displayed correctly", () => {
    const { container } = render(
      <BackgroundContainer>
        <h1>Hello</h1>
        <p>World</p>
      </BackgroundContainer>
    );

    // Get the BackgroundContainer component using the tag div.
    const backgroundContainer = container.querySelector("div");

    // Check if the BackgroundContainer component is defined.
    expect(backgroundContainer).toBeDefined();

    // Check if the BackgroundContainer component has only 2 childs.
    expect(backgroundContainer.childElementCount).toBe(2);

    // Check if the BackgroundContainer component has the className "bg-theThing".
    expect(backgroundContainer.classList.contains("bg-theThing")).toBe(true);

    // Get the h1 tag in the BackgroundContainer component using the text "Hello".
    const title = within(backgroundContainer).getByText("Hello");

    // Check if the h1 tag is defined.
    expect(title).toBeDefined();

    // Check if the h1 tag is really a h1 tag.
    expect(title.tagName).toBe("H1");

    // Get the p tag in the BackgroundContainer component using the text "World".
    const paragraph = within(backgroundContainer).getByText("World");

    // Check if the p tag is defined.
    expect(paragraph).toBeDefined();

    // Check if the p tag is really a p tag.
    expect(paragraph.tagName).toBe("P");
  });
});
