import { useContext, useEffect, useState } from 'react';
import Button from '../components/Button/Button.jsx';
import { UserAndMatchContext } from '../utils/context/UserAndMatchProvider.jsx';
import useNavigation from '../utils/hooks/useNavigation';
import CenteredContainer from '../components/CenteredContainer/CenteredContainer';
import InputWithLabel from '../components/InputWithLabel/InputWithLabel.jsx';

const getAndSetMatchInfo = async (
	matchId,
	setMatchName,
	setMaxPlayers,
	setMinPlayers,
	redirectToMatchList
) => {
	try {
		const resGetInfoMatch = await fetch(
			`http://127.0.0.1:8000/partidas/${matchId}`,
			{
				method: 'GET',
			}
		);

		if (resGetInfoMatch.status === 404) redirectToMatchList();

		if (!resGetInfoMatch.ok) throw new Error('Ha ocurrido un error');

		const dataGetInfoMatch = await resGetInfoMatch.json();

		setMatchName(dataGetInfoMatch.nombre_partida);
		setMaxPlayers(dataGetInfoMatch.max_jugadores);
		setMinPlayers(dataGetInfoMatch.min_jugadores);
	} catch (error) {
		console.log(error.message);
	}
};

const JoinMatch = () => {
	const [username, setUsername] = useState('');
	const [matchPass, setMatchPass] = useState('');
	const { redirectToLobby, redirectToMatchList } = useNavigation();

	const [isLoading, setIsLoading] = useState(false);
	const [error, setError] = useState('');

	const {
		matchInfo,
		setMatchName,
		setUserID,
		setIsCreator,
		setMaxPlayers,
		setMinPlayers,
	} = useContext(UserAndMatchContext);

	useEffect(() => {
		getAndSetMatchInfo(
			matchInfo.id,
			setMatchName,
			setMaxPlayers,
			setMinPlayers,
			redirectToMatchList
		);
	}, []);

	const handleSubmit = async () => {
		try {
			setError('');
			if (username === '')
				throw new Error('Por favor escriba un nombre de usuario');

			setIsLoading(true);

			const body = {
				nombre_jugador: username,
				contraseña: matchPass,
			};

			const resPostUserInfo = await fetch(
				`http://127.0.0.1:8000/partidas/${matchInfo.id}/unir`,
				{
					method: 'POST',
					body: JSON.stringify(body),
					headers: {
						'Content-Type': 'application/json',
					},
				}
			);

			if (resPostUserInfo.status === 400)
				throw new Error('La contraseña es incorrecta');

			if (!resPostUserInfo.ok)
				throw new Error('Ha ocurrido un error, intente mas tarde');

			const dataPostUserInfo = await resPostUserInfo.json();

			setUserID(dataPostUserInfo.id_jugador);
			setIsCreator(false);

			redirectToLobby(matchInfo.id);
		} catch (error) {
			setError(error.message);
			setIsLoading(false);
		}
	};

	return (
		<CenteredContainer>
			<span className="drop-shadow text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-green-700 font-fontgood text-center text-2xl">
				Unirse a Partida: {matchInfo.name}
			</span>
			<hr className=" border border-black/60 drop-shadow" />

			<InputWithLabel
				type="text"
				labelText="Nombre de usuario"
				placeholder="Ej: La Cosa"
				maxLength={16}
				handleChange={(e) => setUsername(e.target.value)}
			/>

			<InputWithLabel
				type="password"
				labelText="Contraseña"
				labelSecondaryText="(opcional)"
				maxLength={32}
				handleChange={(e) => setMatchPass(e.target.value)}
			/>

			<span className="text-red-500 font-semibold drop-shadow w-80">
				{error}
			</span>
			<div className="justify-self-center mt-2">
				{isLoading ? (
					<svg
						className="w-8 h-8 mr-2 text-black/5 animate-spin fill-green-400"
						viewBox="0 0 100 101"
						fill="none"
						xmlns="http://www.w3.org/2000/svg"
					>
						<path
							d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z"
							fill="currentColor"
						/>
						<path
							d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z"
							fill="currentFill"
						/>
					</svg>
				) : (
					<div className="flex justify-center">
						<Button
							text={'Unirse'}
							handleClick={handleSubmit}
							textColor={'text-black'}
							bgColor={'bg-white'}
						/>
						<div style={{ width: '100px' }}></div>
						<Button
							text={'Cancelar'}
							handleClick={redirectToMatchList}
							textColor={'text-black'}
							bgColor={'bg-white'}
						/>
					</div>
				)}
			</div>
		</CenteredContainer>
	);
};

export default JoinMatch;
