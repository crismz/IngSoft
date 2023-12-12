import {
  beforeAll,
  describe,
  test,
  expect,
  vi,
  afterAll,
  afterEach,
} from "vitest";
import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import InputWithLabel from "./InputWithLabel";

describe("Test InputWithLabel component without secondary text", () => {
  beforeAll(() => {
    render(
      <InputWithLabel
        type="text"
        labelText="Username:"
        placeholder="Ej: Light_Yagami"
        maxLength={32}
        handleChange={(e) => console.log(e.target.value)}
      />
    );
  });

  afterAll(() => {
    cleanup();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  const getLabelAndInput = () => {
    const label = screen.getByText("Username:");
    const input = screen.getByPlaceholderText("Ej: Light_Yagami");
    return { label, input };
  };

  test("The component is being displayed correctly", () => {
    const { label, input } = getLabelAndInput();

    // Check if the label tag is defined.
    expect(label).toBeDefined();

    // Check if the label tag is really a label tag.
    expect(label.tagName).toBe("LABEL");

    // Check if the label tag doesn't contain a span tag.
    expect(label.querySelector("span")).toBeNull();

    // Get the htmlFor atribute value from the label.
    const labelHtmlForValue = label.getAttribute("for");

    // Check if the label tag has htmlFor atribute.
    expect(labelHtmlForValue).not.toBeNull();

    // Check if the input tag is defined.
    expect(input).toBeDefined();

    // Check if the input tag is really a input tag.
    expect(input.tagName).toBe("INPUT");

    // Check if the maxLength atribute of the input tag is 32.
    expect(parseInt(input.getAttribute("maxLength"))).toBe(32);

    // Check if the type atribute of the input tag is "text".
    expect(input.getAttribute("type")).toBe("text");

    const inputID = input.getAttribute("id");

    // Check if the id of the input label exists.
    expect(inputID).not.toBeNull();

    // Check if the inputID and the labelHtmlForValue have the same value.
    expect(inputID).toBe(labelHtmlForValue);
  });

  test("The input tag handles changes properly", async () => {
    // Mock the console.log function.
    const consoleLogMock = vi
      .spyOn(console, "log")
      .mockImplementation(() => undefined);

    // Get the input tag.
    const input = screen.getByPlaceholderText("Ej: Light_Yagami");

    // Simulate to write "Lawliet" in the input.
    await userEvent.type(input, "Lawliet");

    // Check if the console.log have received "Lawliet" as argument.
    expect(consoleLogMock).toHaveBeenLastCalledWith("Lawliet");
  });

  test("The label tag focuses the input tag", async () => {
    const { label, input } = getLabelAndInput();

    // Simulate an user click in label.
    await userEvent.click(label);

    // Check if the focus element in the DOM is the input tag.
    expect(document.activeElement).toBe(input);

  });
});

describe("Test InputWithLabel component with secondary text", () => {
  test("The component shows the labelSecondaryText value", () => {
    render(
      <InputWithLabel
        type="text"
        labelText="Username"
        labelSecondaryText="(optional):"
        placeholder="Ej: Okabe_Rintaro"
        maxLength={64}
        handleChange={(e) => console.log(e.target.value)}
      />
    );

    // Get the label tag.
    const label = screen.getByText("Username");

    // Check if the label tag is defined.
    expect(label).toBeDefined();

    // Check if the label tag is really a label tag.
    expect(label.tagName).toBe("LABEL");

    // Get the span tag that is inner the label.
    const innerSpan = label.querySelector("span");

    // Check if the label tag contains the span tag.
    expect(innerSpan).not.toBeNull();

    // Check if the inner span tag contains the text "(optional):".
    expect(innerSpan.textContent).toBe("(optional):");
  });
});
