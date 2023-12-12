import { useContext } from "react";
import { TargetContext } from "../../utils/context/TargetProvider";
import { UserAndMatchContext } from "../../utils/context/UserAndMatchProvider";

const PlayerBox = ({ playerData, playerTurnID }) => {
  const { userInfo } = useContext(UserAndMatchContext);
  const { targetID } = useContext(TargetContext);

  const isCurrentUser = playerData.id_jugador === userInfo.id;
  const isPlayerTurn = playerData.id_jugador === playerTurnID;
  const isTarget = playerData.id_jugador === targetID;

  const getStylesExternDiv = () => {
    if (!isCurrentUser && !isPlayerTurn) return "text-white/70";
    else if (!isCurrentUser && isPlayerTurn) return "flex-col";

    return `absolute scale-125 bottom-5 mb-2 right-14 text-white/90 ${
      isPlayerTurn ? "flex-col" : "text-white/90"
    }`;
  };

  const getStylesInternDiv = () => {
    if (!isCurrentUser && !isPlayerTurn)
      return "bg-black/60 text-white-400 border-gray-300/60";
    else if (!isCurrentUser && isPlayerTurn)
      return "bg-black/40 text-cyan-200 from-blue-600/30 via-black/70 to-black/70 bg-gradient-to-tl border-cyan-400/60";
    else if (isCurrentUser && !isPlayerTurn)
      return "bg-black/70 text-white-400 border-gray-300/60";

    return "text-cyan-200  bg-black/40 from-blue-600/30 via-black/70 to-black/70 bg-gradient-to-tl border-cyan-400/60";
  };

  return (
    <div className={getStylesExternDiv()}>
      {isTarget && <p>↓</p>}
      {isPlayerTurn && (
        <h2 className="p-1 m-1 bg-black/50 text-center rounded-xl text-cyan-500">
          {isCurrentUser ? "Mi turno" : "En turno"}
        </h2>
      )}
      <div className={`p-2 m-2 rounded-md overflow-hidden hover:overflow-visible hover:h-max w-24 h-11 text-center break-words border ${getStylesInternDiv()}`}>
        <span className="line-clamp-1 hover:line-clamp-none ">
         {playerData.nombre_jugador}
        </span>
        
      </div>
      <div>
        {playerData.tiene_cuarentena ? (
          <h2 className="p-1 m-1 bg-black/50 text-center text-base rounded-xl text-green-500">
            {"Cuarentena"}
          </h2>
        ) : null}
      </div>
    </div>
  );
};

export default PlayerBox;