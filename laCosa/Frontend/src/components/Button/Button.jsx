const Button = ({ text, handleClick, textColor, bgColor }) => {
	return (
		<button
			onClick={handleClick}
			className={`${bgColor} ${textColor} py-2 px-4 font-fontgood rounded hover:scale-105 duration-200 active:scale-95 shadow select-none`}
		>
			{text}
		</button>
	);
};

export default Button;
