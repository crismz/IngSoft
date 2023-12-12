import { useContext } from 'react';
import { RoleContext } from '../../utils/context/RoleProvider';

const getRoleText = (role) => {
	const roleDictionary = {
		'La Cosa': {
			roleText: '¡Eres La Cosa!',
			objetive: 'Deshazte de todos los humanos para ganar la partida',
		},
		Humano: {
			roleText: '¡Eres un Humano!',
			objetive:
				'Descubre quien es La Cosa y elimínala. ¡Cuidado con no matar a un humano!',
		},
		Infectado: {
			roleText: '¡Has sido Infectado!',
			objetive: 'Ayuda a La Cosa a ganar la partida',
		},
	};

	return (
		roleDictionary[role] ?? {
			roleText: '',
			objetive: 'No se ha podido obtener el rol',
		}
	);
};

const getColorsByRole = (role) => {
	const colorDictionary = {
		'La Cosa': {
			bgColor: 'from-red-950/75 via-black/75 to-black/75',
			textColor: 'from-red-700 via-red-200 to-white',
			shadowColor: 'shadow-red-700/20',
		},
		Humano: {
			bgColor: 'from-cyan-900/75 via-black/70 to-black/70',
			textColor: 'from-cyan-800 via-cyan-100 to-white',
			shadowColor: 'shadow-cyan-700/20',
		},
		Infectado: {
			bgColor: 'from-lime-950/75 via-black/60 to-black/75',
			textColor: 'from-lime-950 via-lime-200 to-white',
			shadowColor: 'shadow-lime-700/20',
		},
	};
	return (
		colorDictionary[role] ?? {
			bgColor: 'bg-black/75',
			textColor: 'text-white',
			shadowColor: '',
		}
	);
};

const PlayerRole = () => {
	const { role } = useContext(RoleContext);
	const { roleText, objetive } = getRoleText(role);
	const { bgColor, textColor, shadowColor } = getColorsByRole(role);

	return (
		<div
			className={`bg-gradient-to-tl ${bgColor} grid gap-2 absolute top-4 left-4  text-white font-fontgood font-semibold max-w-fit w-[12rem] p-4 shadow-lg ${shadowColor} rounded-md text-center select-none`}
		>
			<span
				className={`bg-clip-text text-transparent bg-gradient-to-tl ${textColor} text-lg`}
			>
				{roleText}
			</span>
			<span
				className={`bg-clip-text text-transparent bg-gradient-to-tl ${textColor} text-sm`}
			>
				{objetive}
			</span>
		</div>
	);
};

export default PlayerRole;
