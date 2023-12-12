import { useNavigate } from 'react-router-dom';

const useNavigation = () => {
	const navigate = useNavigate();

	const redirectToHome = () => navigate('/');
	const redirectToMatchList = () => navigate('/list');
	const redirectToCreateMatch = () => navigate('/create');
	const redirectToJoinMatch = (matchId) => navigate(`/join/${matchId}`);
	const redirectToMatch = (matchId) => navigate(`/match/${matchId}`);
	const redirectToLobby = (matchId) => navigate(`/lobby/${matchId}`);

	return {
		redirectToHome,
		redirectToMatchList,
		redirectToCreateMatch,
		redirectToJoinMatch,
		redirectToMatch,
		redirectToLobby,
	};
};

export default useNavigation;
