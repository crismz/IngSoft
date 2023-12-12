import { useContext, useEffect } from 'react';
import Button from '../Button/Button';
import { UserAndMatchContext } from '../../utils/context/UserAndMatchProvider';
import { RoleContext } from '../../utils/context/RoleProvider';

const DeclareWinButton = ({ playerTurnID }) => {
	const { matchInfo, userInfo } = useContext(UserAndMatchContext);
	const { role, setRole } = useContext(RoleContext);

	const declareWin = async () => {
		try {
			const response = await fetch(
				`http://127.0.0.1:8000/partidas/${matchInfo.id}/jugadores/${userInfo.id}/declarar_victoria`,
				{
					method: 'GET',
				}
			);
			if (!response.ok) throw new Error('Algo salio mal...');
			setRole('');
		} catch (error) {
			console.error(error);
		}
	};

	return (
		<>
			{role === 'La Cosa' && playerTurnID === userInfo.id && (
				<div className="absolute z-50 right-32 bottom-72 scale-125">
					<Button
						text={'Declarar victoria'}
						handleClick={declareWin}
						textColor={'text-white'}
						bgColor={'bg-black/90 border-4 border-red-700'}
					/>
				</div>
			)}
		</>
	);
};

export default DeclareWinButton;
