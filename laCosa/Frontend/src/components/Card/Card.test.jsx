import { afterAll, describe, expect, test } from "vitest";
import { cleanup, render, within } from "@testing-library/react";
import Card from "./Card";

describe("Test the Card component without card data.", () => {
  const exampleCard = {};
  const expectedBgColor = "bg-black/75";

  afterAll(() => {
    cleanup();
  });

  test("The component is being displayed correctly", () => {
    const { container } = render(<Card cardData={exampleCard} />);

    const card = container.querySelector("div");

    // Check if the element is defined
    expect(card).toBeDefined();

    expect(card.classList.contains(expectedBgColor)).toBe(true);
  });
});

describe("Test the Card component with an 'Ataque' card.", () => {
  const exampleCard = {
    id: 0,
    name: "Lanzallamas",
    type: "Accion",
    effectDescription: "Quemar a un jugador adyacente.",
    isSelectable: true,
    isPlayable: true,
    isDisposable: true,
  };

  const expectedTextColor = ["from-lime-950", "via-lime-200", "to-white"];
  const expectedBgColor = ["from-lime-950/75", "via-black/75", "to-black/75"];

  afterAll(() => {
    cleanup();
  });

  test("The component is being displayed correctly", () => {
    const { container } = render(<Card cardData={exampleCard} />);

    const card = container.querySelector("div");

    // Check if the element is defined
    expect(card).toBeDefined();

    expect(
      expectedBgColor.every((className) => card.classList.contains(className))
    ).toBe(true);

    const titleCard = within(card).getByText("Lanzallamas");

    expect(titleCard).toBeDefined();

    expect(
      expectedTextColor.every((className) =>
        titleCard.classList.contains(className)
      )
    ).toBe(true);

    const descriptionCard = within(card).getByText(
      "Quemar a un jugador adyacente."
    );

    expect(descriptionCard).toBeDefined();
  });
});

describe("Test the Card component with an 'Defensa' card.", () => {
  const exampleCard = {
    id: 1,
    name: "Nada de barbacoas",
    type: "Defensa",
    effectDescription: "Defenderse del lanzallamas.",
    isSelectable: true,
    isPlayable: true,
    isDisposable: true,
  };

  const expectedTextColor = ["from-cyan-700", "via-cyan-200", "to-white"];
  const expectedBgColor = ["from-cyan-950/75", "via-black/70", "to-black/70"];

  afterAll(() => {
    cleanup();
  });

  test("The component is being displayed correctly", () => {
    const { container } = render(<Card cardData={exampleCard} />);

    const card = container.querySelector("div");

    // Check if the element is defined
    expect(card).toBeDefined();

    expect(
      expectedBgColor.every((className) => card.classList.contains(className))
    ).toBe(true);

    const titleCard = within(card).getByText("Nada de barbacoas");

    expect(titleCard).toBeDefined();

    expect(
      expectedTextColor.every((className) =>
        titleCard.classList.contains(className)
      )
    ).toBe(true);

    const descriptionCard = within(card).getByText(
      "Defenderse del lanzallamas."
    );

    expect(descriptionCard).toBeDefined();
  });
});
