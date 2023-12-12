import { useContext, useEffect, useState } from "react";
import { UserAndMatchContext } from "../../utils/context/UserAndMatchProvider.jsx";
import Button from "../Button/Button.jsx";
import Card from "../Card/Card";
import { PositionsContext } from "../../utils/context/PositionsProvider.jsx";

const ShowOtherPlayerCards = ({ eventSource }) => {
  const [cardsList, setCardsList] = useState([]);
  const { userInfo} = useContext(UserAndMatchContext);
  const [showCards, setShowCards] = useState(false);
  const [playerShowCardsName, setPlayerShowCardsName] = useState(null);
  const { playersPositions } = useContext(PositionsContext);

  const buttonStyle = {
    bgColor: "bg-white",
    textColor: "text-black",
  };

  useEffect(() => {
    eventSource.addEventListener("Cartas_mostrables", (event) => {
      const data = JSON.parse(event.data);
      setCardsList(data.cartas);
      const playerShowingCard =
        playersPositions.find(
        (player) => player.id_jugador === data.id_jugador
        ) || undefined;
      if (playerShowingCard) setPlayerShowCardsName(playerShowingCard.nombre_jugador);
      if (data.id_jugador !== userInfo.id) setShowCards(true);
      
    });
  }, [playersPositions]);

  return (
    showCards && (
      <div className="absolute scale-75 right-8 top-16 font-fontgood max-h-screen gap-4 flex flex-col justify-center items-center text-center py-10 px-10 bg-black/90 border-2 border-cyan-500">
        <Button
          text="Cerrar"
          handleClick={() => setShowCards(false)}
          {...buttonStyle}
        />

        <div className="flex gap-4">
          {cardsList.slice(0, 2).map((cardData) => (
            <li key={cardData.id}>
              <Card cardData={cardData} />
            </li>
          ))}
        </div>
        <div className="flex gap-4">
          {cardsList.slice(2, 4).map((cardData) => (
            <li key={cardData.id}>
              <Card cardData={cardData} />
            </li>
          ))}
        </div>
        <h2 className="text-white">
          Cartas de {playerShowCardsName}
        </h2>
      </div>
    )
  );
};

export default ShowOtherPlayerCards;
