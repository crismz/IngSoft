// Ahora usando el nuevo contexto de mano de fin de turno

import { useContext, useEffect, useState } from "react";
import { UserAndMatchContext } from "../../utils/context/UserAndMatchProvider.jsx";
import Button from "../Button/Button.jsx";

const RevelationCard = ({ eventSource }) => {
  const [IDPlayerChoosing, setIDPlayerChoosing] = useState(-1);
  const { matchInfo, userInfo } = useContext(UserAndMatchContext);

  useEffect(() => {
    eventSource.addEventListener("Revelar", (event) => {
      const data = JSON.parse(event.data);
      setIDPlayerChoosing(data.id_jugador);
    });
  }, []);

  const handleRevealChoice = async (reveal) => {
		setIDPlayerChoosing(-1);
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/partidas/${matchInfo.id}/jugadores/${userInfo.id}/revelar`,
        {
          method: "PUT",
          body: JSON.stringify({
            revela: reveal,
          }),
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
      if (!response.ok) throw new Error("Algo salió mal...");
    } catch (error) {
      console.error(error);
    }
  };

  return (
    userInfo.id === IDPlayerChoosing && (
      <div className="absolute left-36 gap-2 top-56 font-fontgood max-h-screen flex flex-col justify-center items-center text-center py-6 px-6 w-96 bg-black/90 border-2 border-cyan-500">
        <h2 className="text-white text-2xl">
					Se ha jugado la carta "Revelaciones"
				</h2>
        <h2 className=" text-gray-200">
          Es tu turno de elegir si mostrar o no tu mano.
        </h2>
        <h2 className=" text-sm text-gray-400">
          La ronda de Revelaciones finalizara cuando alguien muestre una carta
          de "Infectado" o si termina la ronda
        </h2>
				
        <div className="z-50 gap-6 flex">
          
					<Button
            text={"Mostrar"}
            handleClick={() => handleRevealChoice(true)}
            textColor={"text-white"}
            bgColor={"bg-black/90 border-2 border-white"}
          />
          <Button
            text={"No mostrar"}
            handleClick={() => handleRevealChoice(false)}
            textColor={"text-white"}
            bgColor={"bg-black/90 border-2 border-white"}
          />
        </div>
      </div>
    )
  );
};

export default RevelationCard;
