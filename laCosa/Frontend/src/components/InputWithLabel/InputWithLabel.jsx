import { useId } from 'react';

const InputWithLabel = ({
	type,
	labelText,
	labelSecondaryText = undefined,
	placeholder = '',
	maxLength,
	handleChange,
}) => {
	const id = useId();
	return (
		<>
			<label
				htmlFor={id}
				className="drop-shadow text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-green-700 font-fontgood"
			>
				{labelText}{' '}
				{labelSecondaryText && (
					<span className="text-black/40">{labelSecondaryText}</span>
				)}
			</label>
			<input
				placeholder={placeholder}
				required
				maxLength={maxLength}
				className="p-1 shadow rounded-sm px-2 resize-none w-80 bg-black/90"
				type={type}
				id={id}
				onChange={handleChange}
			/>
		</>
	);
};

export default InputWithLabel;
