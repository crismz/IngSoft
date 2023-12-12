import { useContext, useEffect, useState } from "react";
import { UserAndMatchContext } from "../../utils/context/UserAndMatchProvider";
import { PositionsContext } from "../../utils/context/PositionsProvider.jsx";
import { TargetExchangeContext } from "../../utils/context/TargetExchangeProvider.jsx";

const ExchangeForRequestedPlayer = ({ eventSource, playerTurnID }) => {
  const [exchangeRequestInfo, setExchangeRequestInfo] = useState([]);
  const { userInfo } = useContext(UserAndMatchContext);
  const [contextInfo, setContextInfo] = useState([]);
  const { playersPositions } = useContext(PositionsContext);
  const [canExchange, setCanExchange] = useState(false);

  useEffect(() => {
    eventSource.addEventListener("Pedido_intercambio", (event) => {
      setExchangeRequestInfo(JSON.parse(event.data));
    });
  }, []);

  useEffect(() => {
    eventSource.addEventListener("Mano", (event) => {
      const data = JSON.parse(event.data);
      setContextInfo(data.context);
      setCanExchange(false);
    });
  }, []);

  const exchangingWithPlayer =
    playersPositions.find(
      (player) => player.id_jugador === exchangeRequestInfo.id_jugador
    ) || undefined;

  useEffect(() => {
    if (
      exchangingWithPlayer &&
      contextInfo === "Intercambiables_defensa" &&
      userInfo.id !== playerTurnID
    ) {
      setCanExchange(true);
    }
  }, [
    setContextInfo,
    userInfo.id,
    playerTurnID,
    contextInfo,
    playersPositions,
  ]);

  return (
    exchangingWithPlayer &&
    canExchange && (
      <div className="absolute left-36 top-56 font-fontgood max-h-screen gap-4 flex flex-col justify-center items-center text-center py-4 px-8 bg-black/90 border-2 border-cyan-500">
        <h2 className="font-fontgood text-2xl text-green-400 mt-2">
          FASE DE INTERCAMBIO
        </h2>
        <h2 className="font-fontgood text-lg text-white mt-2">
          Intercambiando con:
        </h2>
        <div className="text-white/70 scale-125  mb-2 flex flex-col">
          <div
            className={`bg-black/40 text-cyan-200 from-blue-600/30 via-black/70 to-black/70 bg-gradient-to-tl border-cyan-400/60`}
          >
            {exchangingWithPlayer.nombre_jugador}
          </div>
        </div>
      </div>
    )
  );
};

export default ExchangeForRequestedPlayer;
