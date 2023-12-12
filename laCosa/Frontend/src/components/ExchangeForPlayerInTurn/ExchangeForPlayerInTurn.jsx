import { useContext, useEffect, useState } from "react";
import { PositionsContext } from "../../utils/context/PositionsProvider.jsx";

import { TargetExchangeContext } from "../../utils/context/TargetExchangeProvider.jsx";
import { UserAndMatchContext } from "../../utils/context/UserAndMatchProvider";

const ExchangeForPlayerInTurn = ({ eventSource, playerTurnID }) => {
  const { playersPositions } = useContext(PositionsContext);
  const [contextInfo, setContextInfo] = useState([]);
  const { targetExchangeID, setTargetExchangeID } = useContext(
    TargetExchangeContext
  );
  const { userInfo } = useContext(UserAndMatchContext);
  const [canExchange, setCanExchange] = useState(false);
  const [exchangingWithNAME, setExchangingWithNAME] = useState(null);

  useEffect(() => {
    eventSource.addEventListener("Mano", (event) => {
      const data = JSON.parse(event.data);
      setContextInfo(data.context);
      setCanExchange(false);
    });
  }, []);

  useEffect(() => {
    eventSource.addEventListener("Objetivo_intercambio", (event) => {
      const data = JSON.parse(event.data);
      setTargetExchangeID(data.id_jugador);
    });
  }, []);

  useEffect(() => {
    if (
      (contextInfo === "Intercambiables" ||
        contextInfo === "Vuelta_y_vuelta" ||
        (targetExchangeID !== -1 && contextInfo === "Esperando")) &&
      userInfo.id === playerTurnID
    ) {
      const exchangingWithPlayer =
        userInfo.id === playerTurnID
          ? playersPositions.find(
              (player) => player.id_jugador === targetExchangeID
            ) || undefined
          : undefined;

      if (exchangingWithPlayer) {
        setExchangingWithNAME(exchangingWithPlayer.nombre_jugador);
        setCanExchange(true);
      }
      if (targetExchangeID === -2) {
        setExchangingWithNAME("Mazo");
        setCanExchange(true);
      }
    }
  }, [
    setContextInfo,
    userInfo.id,
    playerTurnID,
    eventSource,
    targetExchangeID,
    contextInfo,
    playersPositions,
  ]);

  return (
    (canExchange && (
      <div className="absolute left-36 top-56 font-fontgood max-h-screen gap-4 flex flex-col justify-center items-center text-center py-4 px-8 bg-black/90 border-2 border-cyan-500">
        <h2 className="font-fontgood text-2xl text-green-400 mt-2">
          FASE DE INTERCAMBIO
        </h2>
        <h2 className="font-fontgood text-lg text-white mt-2">
          Intercambiando con:
        </h2>
        <div className="text-white/70 scale-125  mb-2 flex flex-col">
          <div
            className={`p-2 m-2 rounded-md text-center border bg-black/60 text-white-400 border-gray-300/60`}
          >
            {exchangingWithNAME}
          </div>
        </div>
      </div>
    )) ||
    (contextInfo === "Vuelta_y_vuelta" && (
      <div className="absolute left-36 top-56 font-fontgood max-h-screen gap-4 flex flex-col justify-center items-center text-center py-4 px-8 bg-black/90 border-2 border-cyan-500">
        <h2 className="font-fontgood text-2xl text-green-400 mt-2">
          FASE DE INTERCAMBIO
        </h2>
        <h2 className="font-fontgood text-lg text-white mt-2">
          Se ha jugado Vuelta y Vuelta:
        </h2>
        <div className="text-white/70 text-sm w-80 scale-125 truncate mb-2 flex flex-col">
          Elige una carta para darle al siguiente jugador
        </div>
      </div>
    ))
  );
};

export default ExchangeForPlayerInTurn;
