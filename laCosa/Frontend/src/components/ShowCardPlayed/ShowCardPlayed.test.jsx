import { afterAll, describe, expect, test } from 'vitest';
import { cleanup, render, screen } from '@testing-library/react';
import ShowCardPlayed from './ShowCardPlayed';
import { createMockEventSource } from '../../utils/functions/createMockEventSource.js';

describe('Test the ShowCardPlayed component without a card', () => {
	const mockEventSource = createMockEventSource({ carta: {} });

	afterAll(() => {
		cleanup();
	});

	test('The component is being displayed correctly', () => {
		render(<ShowCardPlayed eventSource={mockEventSource} />);

		// The status of the card is being displayed well.
		const statusCard = screen.getByText('No hay carta jugada');

		expect(statusCard).not.toBeNull();

		expect(statusCard.tagName).toBe('H2');
	});
});

describe('Test the ShowCardPlayed component with a hardcoded card', () => {
	const mockEventSource = createMockEventSource({
		carta: {
			id: 0,
			name: 'Lanzallamas',
			type: 'Accion',
			effectDescription: 'Quemar a un jugador adyacente.',
			isSelectable: true,
			isPlayable: true,
			isDisposable: true,
		},
	});

	afterAll(() => {
		cleanup();
	});

	test('The component is being displayed correctly', () => {
		render(<ShowCardPlayed eventSource={mockEventSource} />);

		// The status of the card is being displayed well.
		const statusCard = screen.getByText('Carta jugada');

		expect(statusCard).not.toBeNull();

		expect(statusCard.tagName).toBe('H2');

		// The name of the card is being displayed well.
		const cardName = screen.getByText('Lanzallamas');

		expect(cardName).not.toBeNull();

		// The description of the card is being displayed well.
		const cardDescription = screen.getByText('Quemar a un jugador adyacente.');

		expect(cardDescription).not.toBeNull();
	});
});
