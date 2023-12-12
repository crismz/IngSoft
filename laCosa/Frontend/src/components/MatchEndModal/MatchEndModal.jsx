import { useContext, useEffect, useState } from 'react';
import Button from '../Button/Button';
import useNavigation from '../../utils/hooks/useNavigation';
import { UserAndMatchContext } from '../../utils/context/UserAndMatchProvider';

const getWinnerTextAndColor = (winner) => {
	const textDictionary = {
		Humanos: {
			bottomText: 'Son los ganadores',
			winnerText: 'Los Humanos',
			bgColor: 'from-cyan-950/75 via-black/70 to-black/70',
			textColor: 'from-cyan-800 via-cyan-200 to-white',
		},
		Infectados: {
			bottomText: 'Son los ganadores',
			winnerText: 'Los Infectados',
			bgColor: 'from-lime-950/75 via-black/60 to-black/75',
			textColor: 'from-lime-950 via-lime-300 to-white',
		},
		'La Cosa': {
			bottomText: 'Ha ganado la partida',
			winnerText: 'La Cosa',
			bgColor: 'from-red-950/75 via-black/75 to-black/75',
			textColor: 'from-red-700 via-red-300 to-white',
		},
	};

	return (
		textDictionary[winner] ?? {
			bottomText: '',
			winnerText: 'No se ha podido determinar el ganador',
			bgColor: 'bg-black/75',
			textColor: 'text-white',
		}
	);
};

const getWinContext = (context) => {
	const contextDictionary = {
		CosaMuerta: '¡La Cosa ha muerto!',
		MalDeclaracion:
			'La Cosa ha revelado su identidad mientras aun habia humanos vivos...',
		NoHumanos: 'Han muerto todos los humanos...',
		TodosInfectados: '¡Todos los humanos han sido infectados!',
	};

	return (
		contextDictionary[context] ?? {
			context: 'No se ha podido determinar el contexto de la victoria',
		}
	);
};

const MatchEndModal = ({ eventSource }) => {
	const [bottomText, setBottomText] = useState('');
	const [winnerText, setWinnerText] = useState('');
	const [bgColor, setBgColor] = useState('');
	const [textColor, setTextColor] = useState('');
	const [winContext, setWinContext] = useState('');

	const { redirectToHome } = useNavigation();

	const { resetUserAndMatchState } = useContext(UserAndMatchContext);

	useEffect(() => {
		eventSource.addEventListener('Finalizo_partida', (event) => {
			const { bottomText, winnerText, bgColor, textColor } =
				getWinnerTextAndColor(JSON.parse(event.data).rol_ganador);
			const winContext = getWinContext(JSON.parse(event.data).contexto);

			setBottomText(bottomText);
			setWinnerText(winnerText);
			setBgColor(bgColor);
			setTextColor(textColor);
			setWinContext(winContext);
		});
	}, []);

	const handleClick = () => {
		eventSource.close();
		resetUserAndMatchState();
		redirectToHome();
	};

	return (
		(bottomText !== '' || winnerText !== '') && (
			<div
				className={`absolute w-screen h-screen bg-black/50 z-50 transition-BlurAndOpacity duration-700 opacity-100 blur-none select-none`}
			>
				<div
					className={`${bgColor} absolute grid grid-cols-1 place-items-center justify-between left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 bg-gradient-to-tl rounded-md shadow-black/60 shadow-xl w-2/6 h-2/6 p-6 `}
				>
					<span className="font-fontgood text-center drop-shadow-md text-white text-lg">
						{winContext}
					</span>
					<span
						className={`${textColor} font-fontgood text-center bg-clip-text text-transparent bg-gradient-to-tl drop-shadow text-6xl`}
					>
						{winnerText}
					</span>
					<span
						className={`${textColor} font-fontgood text-center bg-clip-text text-transparent bg-gradient-to-tl drop-shadow text-2xl`}
					>
						{bottomText}
					</span>
					<div className="">
						<Button
							text={'Volver al inicio'}
							bgColor={'bg-white'}
							textColor={'text-black'}
							handleClick={handleClick}
						/>
					</div>
				</div>
			</div>
		)
	);
};

export default MatchEndModal;
