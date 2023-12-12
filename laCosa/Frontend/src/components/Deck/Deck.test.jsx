import { cleanup, render, screen } from '@testing-library/react';
import { afterAll, beforeAll, describe, expect, vi, test } from 'vitest';
import Deck from './Deck.jsx';
import UserAndMatchProvider from '../../utils/context/UserAndMatchProvider.jsx';
import { createMockEventSource } from '../../utils/functions/createMockEventSource.js';

describe('Test Deck component', () => {
	beforeAll(() => {
		const mockEventSource = createMockEventSource({});

		render(
			<UserAndMatchProvider>
				<Deck
					typeDeck={'deckPanico'}
					canTakeCard={true}
					handleClick={() => console.log('Take a Card.')}
					eventSource={mockEventSource}
				/>
			</UserAndMatchProvider>
		);
	});

	afterAll(() => {
		cleanup();
	});

	const getDeck = () => screen.getByRole('button');

	test('The deck component is being displayed correctly', () => {
		const deck = getDeck();

		// Check if the element is defined
		expect(deck).toBeDefined();

		// Check if the element has the onClick event defined.
		expect(deck.click).toBeDefined();
	});
});
