import { cleanup, render, screen } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, test } from 'vitest';
import HandOfCards from './HandOfCards.jsx';
import userEvent from '@testing-library/user-event';
import UserAndMatchProvider from '../../utils/context/UserAndMatchProvider.jsx';
import TargetProvider from '../../utils/context/TargetProvider.jsx';
import TargetExchangeProvider from '../../utils/context/TargetExchangeProvider.jsx';
import { RoleProvider } from '../../utils/context/RoleProvider.jsx';
import { createMockEventSource } from '../../utils/functions/createMockEventSource.js';

/**
 * @importante
 *
 * Este test funciona gracias a que por el momento el estado
 * cardsOfHand del componente HandOfCards tiene un valor
 * fijo que es exactamente igual que la constante exampleHand
 * que estamos definiendo en este test. En un futuro,
 * cuando obtengamos el valor de cardsOfHand del backend,
 * estos tests dejarán de tener sentido y deberán ser modificados.
 */

describe('Test the HandOfCards component', () => {
	const exampleHand = [
		{
			id: 0,
			name: 'Lanzallamas',
			type: 'Accion',
			effectDescription: 'Quemar a un jugador adyacente.',
			isSelectable: true,
			isPlayable: true,
			isDisposable: true,
		},
		{
			id: 1,
			name: 'Ejemplo carta defensa',
			type: 'Defensa',
			effectDescription: 'Este es un ejemplo xd.',
			isSelectable: true,
			isPlayable: false,
			isDisposable: true,
		},
		{
			id: 2,
			name: 'Ejemplo carta LA COSA',
			type: 'Contagio',
			effectDescription: 'Sos LA COSA',
			isSelectable: false,
			isPlayable: false,
			isDisposable: false,
		},
	];

	beforeEach(() => {
		render(
			<UserAndMatchProvider>
				<TargetProvider>
					<TargetExchangeProvider>
						<RoleProvider>
							<HandOfCards
								eventSource={createMockEventSource({
									cartas: exampleHand,
								})}
							/>
						</RoleProvider>
					</TargetExchangeProvider>
				</TargetProvider>
			</UserAndMatchProvider>
		);
	});

	afterEach(() => {
		cleanup();
	});

	const getCardList = () => screen.getByRole('list');
	const getElementListByIndex = (index) =>
		screen.getAllByRole('listitem')[index];

	test('The component is being displayed correctly', () => {
		const cardList = getCardList();

		// Check if all elements of exampleHand are rendering
		expect(cardList.childElementCount).toBe(exampleHand.length);

		// Check if all elements are li and contain a button (Card component)
		exampleHand.forEach((_, index) => {
			const listItem = getElementListByIndex(index);

			expect(listItem.tagName).toBe('LI');
			expect(listItem.firstElementChild.tagName).toBe('BUTTON');
		});

		const buttonPlay = screen.queryByText('Jugar');

		// buttonPlay doesn't exist.
		expect(buttonPlay).toBeNull();

		const buttonDisposable = screen.queryByText('Descartar');

		// buttonDisposable doesn't exist.
		expect(buttonDisposable).toBeNull();
	});

	test('The card is being selected successfully when isPlayable and isDisposable are true', async () => {
		const lanzallamasCard = getElementListByIndex(0).firstElementChild;

		await userEvent.click(lanzallamasCard);

		const buttonPlay = screen.queryByText('Jugar');

		// buttonPlay exists.
		expect(buttonPlay).not.toBeNull();

		const buttonDisposable = screen.queryByText('Descartar');

		// buttonDisposable exists.
		expect(buttonDisposable).not.toBeNull();
	});

	test('The card is being selected successfully when isPlayable is false and isDisposable is true', async () => {
		const defensaCard = getElementListByIndex(1).firstElementChild;

		await userEvent.click(defensaCard);

		const buttonPlay = screen.queryByText('Jugar');

		// buttonPlay doesn't exist.
		expect(buttonPlay).toBeNull();

		const buttonDisposable = screen.queryByText('Descartar');

		// buttonDisposable exists.
		expect(buttonDisposable).not.toBeNull();
	});

	test("When the isSelectable is false, then the card can't be selected", async () => {
		const laCosaCard = getElementListByIndex(2).firstElementChild;

		await userEvent.click(laCosaCard);

		const buttonPlay = screen.queryByText('Jugar');

		// buttonPlay doesn't exist.
		expect(buttonPlay).toBeNull();

		const buttonDisposable = screen.queryByText('Descartar');

		// buttonDisposable doesn't exist.
		expect(buttonDisposable).toBeNull();
	});
});
