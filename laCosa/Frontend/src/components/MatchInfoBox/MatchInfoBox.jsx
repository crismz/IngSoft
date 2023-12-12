import { useContext } from 'react';
import useNavigation from '../../utils/hooks/useNavigation.jsx';
import { UserAndMatchContext } from '../../utils/context/UserAndMatchProvider.jsx';

const MatchInfoBox = ({
	matchName,
	isPrivate,
	maxPlayerAmount,
	currentPlayerAmount,
	matchId,
}) => {
	const { redirectToJoinMatch } = useNavigation();

	const { setMatchID } = useContext(UserAndMatchContext);

	const isFull = currentPlayerAmount === maxPlayerAmount;
	const fullTextStyle = isFull ? 'text-red-400' : '';
	const fullHoverStyle = isFull
		? 'cursor-default'
		: 'hover:scale-105 hover:border-white active:scale-100';

	const handleClick = () => {
		if (isFull) return;
		setMatchID(matchId);
		redirectToJoinMatch(matchId);
	};

	return (
		<button
			className={`${fullHoverStyle} bg-black/90 shadow rounded-sm p-2 flex font-fontgood justify-between w-full duration-200 border border-transparent`}
			onClick={handleClick}
		>
			<div className="flex px-1 gap-2 items-center">
				<span>{matchName}</span>
				{isPrivate && (
					<svg
						className="w-[16px] h-[16px] text-white"
						aria-hidden="true"
						xmlns="http://www.w3.org/2000/svg"
						fill="none"
						viewBox="0 0 16 20"
					>
						<path
							stroke="currentColor"
							strokeLinecap="round"
							strokeLinejoin="round"
							strokeWidth="2"
							d="M11.5 8V4.5a3.5 3.5 0 1 0-7 0V8M8 12v3M2 8h12a1 1 0 0 1 1 1v9a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1V9a1 1 0 0 1 1-1Z"
						/>
					</svg>
				)}
			</div>
			<span className={`px-1 ${fullTextStyle}`}>
				{currentPlayerAmount + '/' + maxPlayerAmount}
			</span>
		</button>
	);
};

export default MatchInfoBox;
