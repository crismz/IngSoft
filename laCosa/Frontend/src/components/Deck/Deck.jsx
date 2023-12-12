import { useContext, useEffect, useState } from 'react';
import { UserAndMatchContext } from '../../utils/context/UserAndMatchProvider';

/**
 *
 * @param evetSource - Manejador de eventos
 * @param canTakeCard - Bool que define si se puede sacar una carta o no
 *
 */
const Deck = ({ eventSource, playerTurnID }) => {
	const [deckIsPanic, setDeckIsPanic] = useState({});
	const [isClickable, setIsClickable] = useState(false);

	const { matchInfo, userInfo } = useContext(UserAndMatchContext);

	useEffect(() => {
		eventSource.addEventListener('Mazo', (event) => {
			setDeckIsPanic(JSON.parse(event.data));
		});
	}, []);

	useEffect(() => {
		setIsClickable(playerTurnID === userInfo.id);
	}, [playerTurnID]);

	const typeDeck = deckIsPanic.es_panico ? 'deckPanico' : 'deckAlejate';

	const imagePath = `../images/mazos/${typeDeck}.png`;

	const stealCard = async () => {
		//esto es para que solo saque una carta, pero podria ser mejor que el bool se modifique fuera
		if (isClickable) {
			setIsClickable(false);
			try {
				const response = await fetch(
					`http://127.0.0.1:8000/partidas/${matchInfo.id}/mazo/robar`,
					{
						method: 'PATCH',
						body: JSON.stringify({
							id_jugador: userInfo.id,
							robo_inicio_turno: true,
						}),
						headers: {
							'Content-Type': 'application/json',
						},
					}
				);
				if (!response.ok) throw new Error('Algo salio mal...');
			} catch (error) {
				console.error(error);
			}
		}
	};

	return (
		<button
			className={`flex flex-col font-fontgood font-bold justify-center items-center duration-100 ${
				isClickable ? 'active:scale-95' : 'cursor-default'
			}`}
			onClick={stealCard}
		>
			<h2 className="text-lg">Mazo</h2>
			<img src={imagePath.toString()} alt={typeDeck} width="200px" />
		</button>
	);
};
export default Deck;
