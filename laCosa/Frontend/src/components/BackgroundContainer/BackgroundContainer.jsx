const BackgroundContainer = ({ children }) => {
  return (
    <div className="bg-theThing bg-no-repeat bg-[length:100%_100%] bg-center h-screen w-screen">
      {children}
    </div>
  );
};

export default BackgroundContainer;
