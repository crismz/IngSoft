const CenteredContainer = ({ children }) => {
  return (
    <div className="flex justify-center h-screen items-center">
      <div className="bg-black/80 rounded shadow-md text-white p-6 grid grid-cols-1 gap-3 w-fit">
        {children}
      </div>
    </div>
  );
};

export default CenteredContainer;
