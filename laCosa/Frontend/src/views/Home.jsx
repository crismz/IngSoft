import Button from '../components/Button/Button';
import useNavigation from '../utils/hooks/useNavigation';

const Home = () => {
	const { redirectToCreateMatch, redirectToMatchList } = useNavigation();

	const buttonStyle = {
		bgColor: 'bg-black',
		textColor: 'text-white',
	};

	return (
		<main className="flex flex-col items-center justify-center h-screen">
			<h1 className="text-9xl font-bold mb-10 select-none">La Cosa</h1>
			<div className="space-x-10">
				<Button
					text="Crear partida"
					handleClick={redirectToCreateMatch}
					{...buttonStyle}
				/>
				<Button
					text="Unirse a partida"
					handleClick={redirectToMatchList}
					{...buttonStyle}
				/>
			</div>
		</main>
	);
};

export default Home;
