// Ahora usando el nuevo contexto de mano de fin de turno

import { useContext, useEffect, useState } from "react";
import { UserAndMatchContext } from "../../utils/context/UserAndMatchProvider.jsx";
import Button from "../Button/Button.jsx";
import { TargetExchangeContext } from "../../utils/context/TargetExchangeProvider.jsx";

const EndOfTurnButton = ({ eventSource }) => {
  const [context, setContext] = useState(null);
  const [canChangeTurn, setCanChangeTurn] = useState(false);
  const { matchInfo, userInfo } = useContext(UserAndMatchContext);
  const { setTargetExchangeID } = useContext(TargetExchangeContext);

  useEffect(() => {
    eventSource.addEventListener("Mano", (event) => {
      const data = JSON.parse(event.data);
      setContext(data.context);
      if (data.context === "Fin_Turno") setCanChangeTurn(true);
      console.log(canChangeTurn);
    });
  }, []);

  const handleEndOfTurn = async () => {
    if (canChangeTurn && context === "Fin_Turno") {
      setCanChangeTurn(false);
      //no se si vale la pena hacerlo pero lo hago por las dudas
      setTargetExchangeID(-1);

      try {
        const response = await fetch(
          `http://127.0.0.1:8000/partidas/${matchInfo.id}/finalizar_turno`,
          {
            method: "PATCH",
            headers: {
              "Content-Type": "application/json",
            },
          }
        );
        if (!response.ok) throw new Error("Algo salio mal...");
      } catch (error) {
        console.error(error);
      }
    }
  };

  return (
    <>
      {canChangeTurn && (
        <div className="absolute z-50 right-32 bottom-52 scale-125">
          <Button
            text={"Terminar Turno"}
            handleClick={handleEndOfTurn}
            textColor={"text-white"}
            bgColor={"bg-black/90 border-4 border-red-700"}
          />
        </div>
      )}
    </>
  );
};

export default EndOfTurnButton;

