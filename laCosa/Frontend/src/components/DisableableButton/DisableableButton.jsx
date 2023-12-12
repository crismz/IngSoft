const DisableableButton = ({
  text,
  handleClick,
  disabled,
  textColor = "text-black",
  bgColor = "bg-white",
}) => {
  return (
    <button
      onClick={handleClick}
      className={`${bgColor} ${textColor} py-2 px-4 font-fontgood rounded shadow ${
        disabled
          ? "cursor-not-allowed"
          : "select-none hover:scale-105 duration-200 active:scale-95"
      }`}
      disabled={disabled}
    >
      {text}
    </button>
  );
};

export default DisableableButton;
