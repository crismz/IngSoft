import { createContext, useState } from "react";

export const PositionsContext = createContext();

const PositionsProvider = ({ children }) => {

  const [playersPositions, setPlayersPositions] = useState([]);

  const resetPlayersPositions = () => {
    setOrderedPlayers([]);
  };

  const setManualOrderedPlayers = (newOrderedPlayers) => {
    setPlayersPositions(newOrderedPlayers);
  };

  const providedState = {
    playersPositions,
    setManualOrderedPlayers,
    resetPlayersPositions,
  };

  return (
    <PositionsContext.Provider value={providedState}>
      {children}
    </PositionsContext.Provider>
  );
};

export default PositionsProvider;