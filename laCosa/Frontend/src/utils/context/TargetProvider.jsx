import { createContext, useEffect, useState } from "react";

export const TargetContext = createContext();

const TargetProvider = ({ children }) => {
  const [targetID, setTargetID] = useState(null);

  // can be 'any', 'neighbour', 'self' and '' (the last one represents that it does not require an objective).
  const [targetPositionInfo, setTargetPositionInfo] = useState(null);

  return (
    <TargetContext.Provider
      value={{
        targetID,
        setTargetID,
        targetPositionInfo,
        setTargetPositionInfo,
      }}
    >
      {children}
    </TargetContext.Provider>
  );
};

export default TargetProvider;
