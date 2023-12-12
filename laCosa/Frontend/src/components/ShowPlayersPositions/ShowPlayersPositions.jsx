import React, { useContext, useEffect, useState } from "react";
import { orderPlayersPositions } from "../../utils/functions/orderPlayersPositions.js";
import { UserAndMatchContext } from "../../utils/context/UserAndMatchProvider.jsx";
import PlayerBox from "../PlayerBox/PlayerBox.jsx";
import { PositionsContext } from "../../utils/context/PositionsProvider.jsx";
import { TargetContext } from "../../utils/context/TargetProvider.jsx";
import canBeTarget from "../../utils/functions/canBeTarget.js";
import ButtonSelectTarget from "../ButtonSelectTarget/ButtonSelectTarget.jsx";

const ShowPlayersPositions = ({ eventSource, playerTurnID }) => {
  const { setManualOrderedPlayers } = useContext(PositionsContext);
  const [playersPositionsList, setPlayersPositionsList] = useState([]);
  const { userInfo } = useContext(UserAndMatchContext);
  const { targetID, targetPositionInfo } = useContext(TargetContext);

  useEffect(() => {
    eventSource.addEventListener("Ronda", (event) => {
      const eventData = JSON.parse(event.data);
      setPlayersPositionsList(orderPlayersPositions(eventData.ronda, userInfo.id));
      setManualOrderedPlayers(orderPlayersPositions(eventData.ronda, userInfo.id));
    });
  }, []);

  const imagePath = "../images/puerta_atrancada.png";
  console.log(playersPositionsList);
  return (
    playersPositionsList && (
      <div className="max-h-screen flex flex-col justify-start items-center">
        <h2 className="font-fontgood text-2xl text-white/90 mt-2">
          {playersPositionsList.length !== 0
            ? "Jugadores"
            : "Aun no se distribuyeron los jugadores"}
        </h2>
        <div className="flex items-center text-center font-fontgood box-border gap-2 text-lg">
          <h2 className="p-1 m-1 bg-black/20 rounded-xl text-sm text-white/70">
            Izquierda del jugador
          </h2>
          {playersPositionsList.map((player) => (
            <div className="flex gap-2">
              <ButtonSelectTarget
                key={player.id_jugador}
                playerID={player.id_jugador}
                canBeTarget={canBeTarget(
                  playersPositionsList,
                  targetPositionInfo,
                  player.id_jugador
                )}
              >
                <PlayerBox playerData={player} playerTurnID={playerTurnID} />
              </ButtonSelectTarget>
              <ButtonSelectTarget
                key={player.id_jugador + 100}
                playerID={player.id_jugador + 100}
                canBeTarget={canBeTarget(
                  playersPositionsList,
                  targetPositionInfo === "quarantine_door" ? "door" : "none",
                  player.id_jugador
                )}
              >
                {player.puerta_atrancada_izq ? (
                  player.id_jugador + 100 === targetID ? (
                    <div>
                      <p className="text-white text-sm">↓</p>
                      <img
                        className="object-contain h-auto"
                        src={imagePath}
                        width="35px"
                      />
                    </div>
                  ) : (
                    <img
                      className="object-contain h-auto"
                      src={imagePath}
                      width="40px"
                    />
                  )
                ) : null}
              </ButtonSelectTarget>
            </div>
          ))}
          <h2 className="p-1 m-1 bg-black/20 rounded-xl text-sm text-white/70">
            Derecha del jugador
          </h2>
        </div>
      </div>
    )
  );
};

export default ShowPlayersPositions;
