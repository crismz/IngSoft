import { useContext, useState } from 'react';
import Button from '../components/Button/Button.jsx';
import { UserAndMatchContext } from '../utils/context/UserAndMatchProvider.jsx';
import CenteredContainer from '../components/CenteredContainer/CenteredContainer.jsx';
import useNavigation from '../utils/hooks/useNavigation.jsx';
import InputWithLabel from '../components/InputWithLabel/InputWithLabel.jsx';

const CreateMatch = () => {
	const [matchName, setMatchNameLocal] = useState('');
	const [matchPass, setMatchPass] = useState('');
	const [minPlayers, setMinPlayersLocal] = useState(4);
	const [maxPlayers, setMaxPlayersLocal] = useState(12);
	const [username, setUsername] = useState('');

	const [isLoading, setIsLoading] = useState(false);
	const [error, setError] = useState('');

	const {
		setUserID,
		setIsCreator,
		setMatchID,
		setMatchName,
		setMaxPlayers,
		setMinPlayers,
	} = useContext(UserAndMatchContext);

	const { redirectToLobby, redirectToHome } = useNavigation();

	const playerRange = [4, 5, 6, 7, 8, 9, 10, 11, 12];

	const handleSubmit = async () => {
		try {
			setError('');

			if (matchName === '')
				throw new Error('Por favor escriba un nombre para la partida');
			if (username === '')
				throw new Error('Por favor escriba un nombre de usuario');
			if (minPlayers > maxPlayers) {
				throw new Error(
					'La cantidad minima de jugadores no puede ser mayor a la cantidad maxima'
				);
			}

			setIsLoading(true);

			const body = {
				nombre_partida: matchName,
				contraseña: matchPass,
				max_jugadores: maxPlayers,
				min_jugadores: minPlayers,
				nombre_jugador: username,
			};

			const res = await fetch('http://127.0.0.1:8000/partidas/crear', {
				method: 'POST',
				body: JSON.stringify(body),
				headers: {
					'Content-Type': 'application/json',
				},
			});
			if (!res.ok) throw new Error('Ha ocurrido un error, intente mas tarde');

			const data = await res.json();

			// Global state
			setMatchID(data.id_partida);
			setUserID(data.id_jugador);
			setIsCreator(true);
			setMaxPlayers(maxPlayers);
			setMinPlayers(minPlayers);
			setMatchName(matchName);

			redirectToLobby(data.id_partida);
		} catch (error) {
			if (error.message === 'Failed to fetch') {
				setError('Ha ocurrido un error, intente mas tarde');
			} else {
				setError(error.message);
			}
			setIsLoading(false);
		}
	};

	return (
		<CenteredContainer>
			<span className="drop-shadow text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-green-700 font-fontgood text-center text-2xl">
				Crear Partida
			</span>
			<hr className=" border border-black/60 drop-shadow" />

			<InputWithLabel
				type={'text'}
				labelText={'Nombre de la partida'}
				placeholder={'Ej: Keyboard Cowboys'}
				maxLength={32}
				handleChange={(e) => setMatchNameLocal(e.target.value)}
			/>

			<InputWithLabel
				type={'password'}
				labelText={'Contraseña'}
				labelSecondaryText={'(opcional)'}
				maxLength={32}
				handleChange={(e) => setMatchPass(e.target.value)}
			/>

			<span className="drop-shadow text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-green-700 font-fontgood">
				Cantidad de jugadores
			</span>
			<div className="grid grid-cols-2 mb-1">
				<label
					htmlFor="minPlayers"
					className="drop-shadow text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-green-700 font-fontgood mb-2"
				>
					Minimo
				</label>
				<label
					htmlFor="maxPlayers"
					className="drop-shadow text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-green-700 font-fontgood mb-2 ml-2"
				>
					Maximo
				</label>
				<select
					className="p-1 shadow rounded-sm px-2 resize-none w-36 mr-2 bg-black/90"
					id="minPlayers"
					onChange={(e) => setMinPlayersLocal(parseInt(e.target.value))}
				>
					{playerRange.map((option, index) => {
						return (
							<option key={index} value={option}>
								{option}
							</option>
						);
					})}
				</select>
				<select
					className="p-1 shadow rounded-sm px-2 resize-none w-36 ml-2 bg-black/90"
					id="maxPlayers"
					onChange={(e) => setMaxPlayersLocal(parseInt(e.target.value))}
				>
					{playerRange.reverse().map((option, index) => {
						return (
							<option key={index} value={option}>
								{option}
							</option>
						);
					})}
				</select>
			</div>

			<InputWithLabel
				type={'text'}
				labelText={'Nombre de usuario'}
				placeholder={'Ej: La Cosa'}
				maxLength={16}
				handleChange={(e) => setUsername(e.target.value)}
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
							text={'Crear'}
							handleClick={handleSubmit}
							textColor={'text-black'}
							bgColor={'bg-white'}
						/>
						<div style={{ width: '100px' }}></div>
						<Button
							text={'Cancelar'}
							handleClick={redirectToHome}
							textColor={'text-black'}
							bgColor={'bg-white'}
						/>
					</div>
				)}
			</div>
		</CenteredContainer>
	);
};

export default CreateMatch;
