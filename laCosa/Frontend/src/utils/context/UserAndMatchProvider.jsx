import { createContext, useEffect, useState } from "react";

export const UserAndMatchContext = createContext();

const UserAndMatchProvider = ({ children }) => {
  const [userID, setUserID] = useState(() => {
    const storedUserID = sessionStorage.getItem("userID");
    return storedUserID ? parseInt(storedUserID, 10) : -1;
  });

  const [isCreator, setIsCreator] = useState(() => {
    const storedIsCreator = sessionStorage.getItem("isCreator");
    return storedIsCreator ? JSON.parse(storedIsCreator) : false;
  });

  const [matchID, setMatchID] = useState(() => {
    const storedMatchID = sessionStorage.getItem("matchID");
    return storedMatchID ? parseInt(storedMatchID, 10) : -1;
  });

  const [matchName, setMatchName] = useState(() => {
    const storedMatchName = sessionStorage.getItem("matchName");
    return storedMatchName ? storedMatchName : "";
  });

  const [maxPlayers, setMaxPlayers] = useState(() => {
    const storedMaxPlayers = sessionStorage.getItem("maxPlayers");
    return storedMaxPlayers ? parseInt(storedMaxPlayers, 10) : -1;
  });

  const [minPlayers, setMinPlayers] = useState(() => {
    const storedMinPlayers = sessionStorage.getItem("minPlayers");
    return storedMinPlayers ? parseInt(storedMinPlayers, 10) : -1;
  });

  const resetUserAndMatchState = () => {
    sessionStorage.removeItem("userID");
    sessionStorage.removeItem("isCreator");
    sessionStorage.removeItem("matchID");
    sessionStorage.removeItem("matchName");
    sessionStorage.removeItem("maxPlayers");
    sessionStorage.removeItem("minPlayers");

    setUserID(-1);
    setIsCreator(false);
    setMatchID(-1);
    setMatchName("");
    setMaxPlayers(-1);
    setMinPlayers(-1);
  };

  useEffect(() => {
    sessionStorage.setItem("userID", userID.toString());
  }, [userID]);

  useEffect(() => {
    sessionStorage.setItem("isCreator", isCreator.toString());
  }, [isCreator]);

  useEffect(() => {
    sessionStorage.setItem("matchID", matchID.toString());
  }, [matchID]);

  useEffect(() => {
    sessionStorage.setItem("matchName", matchName);
  }, [matchName]);

  useEffect(() => {
    sessionStorage.setItem("maxPlayers", maxPlayers.toString());
  }, [maxPlayers]);

  useEffect(() => {
    sessionStorage.setItem("minPlayers", minPlayers.toString());
  }, [minPlayers]);

  const providedState = {
    userInfo: {
      id: userID,
      isCreator,
    },
    matchInfo: {
      id: matchID,
      name: matchName,
      maxPlayers,
      minPlayers,
    },
    setUserID,
    setIsCreator,
    setMatchID,
    setMatchName,
    setMaxPlayers,
    setMinPlayers,
    resetUserAndMatchState,
  };

  return (
    <UserAndMatchContext.Provider value={providedState}>
      {children}
    </UserAndMatchContext.Provider>
  );
};

export default UserAndMatchProvider;
