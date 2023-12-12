import {
	afterEach,
	afterAll,
	beforeAll,
	describe,
	expect,
	test,
	vi,
} from 'vitest';
import { cleanup, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import SelectableCard from './SelectableCard';
import TargetProvider from '../../utils/context/TargetProvider';

describe('Test the SelectableCard component when is not selected and is selectable', () => {
	const cardData = {
		id: 0,
		name: 'Lanzallamas',
		type: 'Accion',
		effectDescription: 'Quemar a un jugador adyacente.',
		isSelectable: true,
		isPlayable: true,
		isDisposable: true,
	};

	beforeAll(() => {
		render(
			<TargetProvider>
				<SelectableCard
					cardData={cardData}
					isSelected={false}
					setSelectedCardData={(cardJSON) => console.log(cardJSON)}
				/>
			</TargetProvider>
		);
	});

	afterAll(() => {
		cleanup();
	});

	afterEach(() => {
		vi.restoreAllMocks();
	});

	const getCard = () => screen.getByRole('button');

	const expectedButtonClasses = [
		'hover:border-white',
		'hover:bg-black/60',
		'hover:shadow-black/50',
		'hover:shadow-lg',
		'hover:scale-105',
		'hover:-translate-y-3',
		'cursor-pointer',
		'active:scale-95',
	];

	test('The component is being displayed correctly', () => {
		const card = getCard();

		// Check if the element is defined
		expect(card).toBeDefined();

		expect(
			expectedButtonClasses.every((className) =>
				card.classList.contains(className)
			)
		).toBe(true);
	});

	test('The component is responding appropriately to a click', async () => {
		// Mock the console.log function.
		const consoleLogMock = vi
			.spyOn(console, 'log')
			.mockImplementation(() => undefined);

		const card = getCard();

		// Simulate a click.
		await userEvent.click(card);

		// Check if the console.log have been called once.
		expect(consoleLogMock).toHaveBeenCalledOnce();

		// Check if the console.log have received the cardData as argument.
		expect(consoleLogMock).toHaveBeenLastCalledWith(cardData);
	});
});

describe('Test the SelectableCard component when is selected and is selectable', () => {
	const cardData = {
		id: 0,
		name: 'Lanzallamas',
		type: 'Accion',
		effectDescription: 'Quemar a un jugador adyacente.',
		isSelectable: true,
		isPlayable: true,
		isDisposable: true,
	};

	beforeAll(() => {
		render(
			<TargetProvider>
				<SelectableCard
					cardData={cardData}
					isSelected={true}
					setSelectedCardData={(cardJSON) => console.log(cardJSON)}
				/>
			</TargetProvider>
		);
	});

	afterAll(() => {
		cleanup();
	});

	const getCard = () => screen.getByRole('button');

	const expectedButtonClass = '-translate-y-6';

	test('The component is being displayed correctly', () => {
		const card = getCard();

		// Check if the element is defined
		expect(card).toBeDefined();

		expect(card.classList.contains(expectedButtonClass)).toBe(true);
	});
});

describe('Test the SelectableCard component when is not selected and is not selectable', () => {
	const cardData = {
		id: 2,
		name: 'La Cosa',
		type: 'Contagio',
		effectDescription: 'Sos La Cosa',
		isSelectable: false,
		isPlayable: false,
		isDisposable: false,
	};

	beforeAll(() => {
		render(
			<TargetProvider>
				<SelectableCard
					cardData={cardData}
					isSelected={false}
					setSelectedCardData={(cardJSON) => console.log(cardJSON)}
				/>
			</TargetProvider>
		);
	});

	afterAll(() => {
		cleanup();
	});

	afterEach(() => {
		vi.restoreAllMocks();
	});

	const getCard = () => screen.getByRole('button');

	const expectedButtonClass = 'cursor-not-allowed';

	test('The component is being displayed correctly', () => {
		const card = getCard();

		// Check if the element is defined
		expect(card).toBeDefined();

		expect(card.classList.contains(expectedButtonClass)).toBe(true);
	});

	test('The component does nothing on click because isSelectable is false', async () => {
		// Mock the console.log function.
		const consoleLogMock = vi
			.spyOn(console, 'log')
			.mockImplementation(() => undefined);

		const card = getCard();

		// Simulate a click.
		await userEvent.click(card);

		// Check if console.log has not been called.
		expect(consoleLogMock).not.toHaveBeenCalled();
	});
});
