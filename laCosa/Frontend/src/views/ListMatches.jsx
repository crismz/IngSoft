import { useEffect, useState } from 'react';
import Button from '../components/Button/Button.jsx';
import CenteredContainer from '../components/CenteredContainer/CenteredContainer.jsx';
import MatchInfoBox from '../components/MatchInfoBox/MatchInfoBox.jsx';
import ReloadIcon from '../components/Icons/ReloadIcon.jsx';
import useNavigation from '../utils/hooks/useNavigation.jsx';
import ButtonWithIcon from '../components/ButtonWithIcon/ButtonWithIcon.jsx';

const getMatchList = async (setFilteredList, searchText) => {
	try {
		const res = await fetch('http://127.0.0.1:8000/partidas', {
			method: 'GET',
		});

		if (!res.ok) throw new Error('Ha ocurrido un error.');

		const data = await res.json();

		setFilteredList(
			data.lista.filter((match) =>
				match.nombre_partida.toLowerCase().includes(searchText.toLowerCase())
			)
		);
	} catch (error) {
		console.log(error.message);
	}
};

const ListMatches = () => {
	const [searchText, setSearchText] = useState('');
	const [filteredList, setFilteredList] = useState([]);

	const { redirectToHome } = useNavigation();

	useEffect(() => {
		getMatchList(setFilteredList, searchText);
	}, [searchText]);

	const handleReload = () => {
		getMatchList(setFilteredList, searchText);
	};

	return (
		<CenteredContainer>
			<div className="flex gap-3">
				<input
					className="p-1 shadow rounded-sm px-2 resize-none w-80 bg-black/90 "
					type="text"
					onChange={(e) => setSearchText(e.target.value)}
				/>
				<ButtonWithIcon
					Icon={ReloadIcon}
					textColor={'text-black'}
					bgColor={'bg-white'}
					handleClick={handleReload}
				/>
				<Button
					text={'Volver al inicio'}
					textColor={'text-black'}
					bgColor={'bg-white'}
					handleClick={redirectToHome}
				/>
			</div>
			<ul className="bg-black/50 shadow rounded-sm p-3 flex flex-col gap-2 h-96 overflow-y-scroll no-scrollbar">
				{filteredList.map((match) => {
					return (
						<li key={match.id_partida}>
							<MatchInfoBox
								matchName={match.nombre_partida}
								isPrivate={match.tiene_contraseña}
								maxPlayerAmount={match.max_jugadores}
								currentPlayerAmount={match.jugadores_act}
								matchId={match.id_partida}
							/>
						</li>
					);
				})}
			</ul>
		</CenteredContainer>
	);
};

export default ListMatches;
