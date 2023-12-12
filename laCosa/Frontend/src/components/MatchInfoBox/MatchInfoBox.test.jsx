import { afterAll, beforeAll, describe, expect, test } from 'vitest';
import MatchInfoBox from './MatchInfoBox';
import { cleanup, render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import UserAndMatchProvider from '../../utils/context/UserAndMatchProvider';

describe('Test MatchInfoBox component (match is not full and is private)', () => {
	beforeAll(() => {
		render(
			<UserAndMatchProvider>
				<BrowserRouter>
					<MatchInfoBox
						matchName="Partida de Heber"
						isPrivate={true}
						maxPlayerAmount={12}
						currentPlayerAmount={4}
						matchId={1}
					/>
				</BrowserRouter>
			</UserAndMatchProvider>
		);
	});

	afterAll(() => {
		cleanup();
	});

	const getMatchInfoBox = () => screen.getByRole('button');

	test('The component is being displayed correctly', () => {
		const matchInfoBox = getMatchInfoBox();
		const title = matchInfoBox.firstElementChild.firstElementChild;
		const lastChildInsideDiv = matchInfoBox.firstElementChild.lastElementChild;
		const playerCount = matchInfoBox.lastElementChild;

		// Check if the component is defined
		expect(matchInfoBox).toBeDefined();

		// Check if classes are being applied correctly
		expect(matchInfoBox.classList.toString()).toContain(
			'hover:scale-105 hover:border-white active:scale-100'
		);

		// Check if private icon is present
		expect(lastChildInsideDiv.tagName).toBe('svg');

		// Check if text is displaying correctly
		expect(title.textContent).toBe('Partida de Heber');

		expect(playerCount.textContent).toBe('4/12');
	});
});

describe('Test MatchInfoBox component (match is full and is not private)', () => {
	beforeAll(() => {
		render(
			<UserAndMatchProvider>
				<BrowserRouter>
					<MatchInfoBox
						matchName="Partida de Cristian"
						isPrivate={false}
						maxPlayerAmount={10}
						currentPlayerAmount={10}
						matchId={1}
					/>
				</BrowserRouter>
			</UserAndMatchProvider>
		);
	});

	afterAll(() => {
		cleanup();
	});

	const getMatchInfoBox = () => screen.getByRole('button');

	test('The component is being displayed correctly', () => {
		const matchInfoBox = getMatchInfoBox();
		const lastChildInsideDiv = matchInfoBox.firstElementChild.lastElementChild;
		const playerCount = matchInfoBox.lastElementChild;

		// Check if the component is defined
		expect(matchInfoBox).toBeDefined();

		// Check if classes are being applied correctly
		expect(matchInfoBox.classList.toString()).toContain('cursor-default');

		expect(playerCount.classList.toString()).toContain('text-red-400');

		// Check if the private match icon is not present
		expect(lastChildInsideDiv.tagName).toBe('SPAN');

		// Check if text is displaying correctly
		expect(playerCount.textContent).toBe('10/10');
	});
});
