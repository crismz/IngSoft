import { useContext, useEffect, useState } from 'react';
import { UserAndMatchContext } from '../../utils/context/UserAndMatchProvider.jsx';
import Button from '../Button/Button.jsx';
import useNavigation from '../../utils/hooks/useNavigation.jsx';

const getTextFromContext = (context, killer) => {
	const textDictionary = {
		Quemado: killer + ' te ha quemado vivo con un lanzallamas',
		Superinfeccion: 'Has muerto por superinfección',
	};

	return (
		textDictionary[context] ?? {
			context: 'No se ha podido determinar el contexto de la muerte',
		}
	);
};

const DeathScreen = ({ eventSource }) => {
	const { resetUserAndMatchState } = useContext(UserAndMatchContext);
	const { redirectToHome } = useNavigation();
	const [deathText, setDeathText] = useState('');

	useEffect(() => {
		eventSource.addEventListener('Muerte', (event) => {
			const data = JSON.parse(event.data);

			const deathText = getTextFromContext(data.contexto, data.nombre_jugador);
			setDeathText(deathText);
		});
	}, []);

	const handleClick = () => {
		eventSource.close();
		resetUserAndMatchState();
		redirectToHome();
	};

	return (
		<div className="absolute grid place-items-end right-0 z-30">
			{deathText !== '' && (
				<div className="w-screen h-screen">
					<div className="absolute w-screen h-screen bg-black/60 transition-BlurAndOpacity duration-700 opacity-100 blur-none"></div>

					<div className="absolute flex flex-col justify-between left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 bg-gradient-to-tl rounded-md shadow-black/60 shadow-xl w-2/6 h-2/6 p-6 from-red-950/75 via-black/70 to-black/70">
						<span className="font-fontgood text-4xl text-center drop-shadow-md text-white">
							¡Has muerto!
						</span>
						<span className="font-fontgood text-2xl text-center drop-shadow-md text-white">
							{deathText}
						</span>
						<span className="text-center">
							<Button
								text={'Volver al Inicio'}
								handleClick={handleClick}
								textColor={'text-black font-bold'}
								bgColor={'bg-white'}
							/>
						</span>
					</div>
				</div>
			)}
		</div>
	);
};

export default DeathScreen;
