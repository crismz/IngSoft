import {
  describe,
  test,
  expect,
  beforeAll,
  vi,
  afterAll,
  afterEach,
} from "vitest";
import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import Button from "./Button";

describe("Test the Button component", () => {
  beforeAll(() => {
    render(
      <Button
        text={"Hello world"}
        textColor="text-white"
        bgColor="bg-blue-500"
        handleClick={() => console.log("Bye, cowboy")}
      />
    );
  });

  afterAll(() => {
    cleanup();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  const getButton = () => screen.getByText("Hello world");

  test("The component is being displayed correctly", () => {
    const button = getButton();

    // Check if the button is defined and has the text "Hello world".
    expect(button).toBeDefined();

    // Check if the button has bgColor set correctly.
    expect(button.classList.contains("bg-blue-500")).toBe(true);

    // Check if the button has textColor set correctly.
    expect(button.classList.contains("text-white")).toBe(true);

    // Check if the button has the onClick event defined.
    expect(button.click).toBeDefined();
  });

  test("The component is responding appropriately to a click", async () => {
    // Mock the console.log function.
    const consoleLogMock = vi
      .spyOn(console, "log")
      .mockImplementation(() => undefined);

    const button = getButton();

    // Simulate a click.
    await userEvent.click(button);

    // Check if the console.log have been called once.
    expect(consoleLogMock).toHaveBeenCalledOnce();

    // Check if the console.log have received "Bye, cowboy" as argument.
    expect(consoleLogMock).toHaveBeenLastCalledWith("Bye, cowboy");
  });
});
