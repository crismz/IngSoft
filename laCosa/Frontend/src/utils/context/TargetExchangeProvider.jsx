import { createContext, useEffect, useState } from "react";

export const TargetExchangeContext = createContext();

const TargetExchangeProvider = ({ children }) => {
  const [targetExchangeID, setTargetExchangeID] = useState(null);

  useEffect(() => {
    setTargetExchangeID(null);
  }, []);

  return (
    <TargetExchangeContext.Provider
      value={{
        targetExchangeID,
        setTargetExchangeID,
      }}
    >
      {children}
    </TargetExchangeContext.Provider>
  );
};

export default TargetExchangeProvider;
