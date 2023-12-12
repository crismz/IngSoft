const ToggleButton = ({ text, active, onClick }) => {
  return (
    <button
      className={`p-1 w-full ${active ? "bg-white text-black" : "text-white"}`}
      onClick={onClick}
    >
      {text}
    </button>
  );
};

export default ToggleButton;
