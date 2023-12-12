import { useEffect, useState } from "react";
import Card from "../Card/Card";

const ShowCardPlayed = ({ eventSource }) => {
  const [cardPlayedInfo, setCardPlayedInfo] = useState({});

  useEffect(() => {
    eventSource.addEventListener("Carta_jugada", (event) => {
      const data = JSON.parse(event.data)
      setCardPlayedInfo(data.carta);
    });
  }, []);

  return (
    <div className="flex flex-col justify-center items-center">
      <h2 className="font-fontgood font-bold">
        {Object.keys(cardPlayedInfo).length !== 0
          ? "Carta jugada"
          : "No hay carta jugada"}
      </h2>
      <Card cardData={cardPlayedInfo} />
    </div>
  );
};

export default ShowCardPlayed;
