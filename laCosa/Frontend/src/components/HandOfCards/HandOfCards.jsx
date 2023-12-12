import { useCallback, useContext, useEffect, useState } from "react";
import { UserAndMatchContext } from "../../utils/context/UserAndMatchProvider.jsx";
import Button from "../Button/Button.jsx";
import SelectableCard from "../SelectableCard/SelectableCard.jsx";
import { TargetContext } from "../../utils/context/TargetProvider.jsx";
import { TargetExchangeContext } from "../../utils/context/TargetExchangeProvider.jsx";
import { RoleContext } from "../../utils/context/RoleProvider.jsx";

const HandOfCards = ({ eventSource, playerTurnID }) => {
  const [cardsInHand, setCardsInHand] = useState([]);
  const [selectedCardData, setSelectedCardData] = useState(null);
  const { userInfo, matchInfo } = useContext(UserAndMatchContext);
  const [showDefenseButtons, setShowDefenseButtons] = useState(false);
  const [context, setContext] = useState(null);
  const [cardIsNotValid, setCardIsNotValid] = useState(false);
  const { targetID, setTargetID } = useContext(TargetContext);
  const { targetExchangeID } = useContext(TargetExchangeContext);
  const { setRole } = useContext(RoleContext);

	const disposeCard = useCallback(async (cardID) => {
		try {
			const response = await fetch(
				`http://127.0.0.1:8000/partidas/${matchInfo.id}/jugadores/${userInfo.id}/descartar?id_carta=${cardID}`,
				{
					method: 'PATCH',
					headers: {
						'Content-Type': 'application/json',
					},
				}
			);

			if (!response.ok)
				throw new Error('Algo salió mal. Intenta de nuevo más tarde');
		} catch (error) {
			setCardIsNotValid(true);
			console.error(error);
		}
	}, []);
  
  async function exchangeCard(cardID) {
    // ONLY WHHEN PLAYING VUELTA Y VUELTA
    if (context === "Vuelta_y_vuelta") {
      try {
        const response = await fetch(
          `http://127.0.0.1:8000/partidas/${matchInfo.id}/jugadores/${userInfo.id}/vuelta_y_vuelta`,
          {
            method: "PATCH",
            body: JSON.stringify({
              id_carta: cardID,
            }),
            headers: {
              "Content-Type": "application/json",
            },
          }
        );

        if (!response.ok)
          throw new Error("Algo salió mal. Intenta de nuevo más tarde");
      } catch (error) {
        console.error(error);
        setCardIsNotValid(true);
      }
      return;
    }
    // ANY OTHER CASE
    if (userInfo.id === playerTurnID) {
      if (!targetExchangeID && targetExchangeID !== 0) {
        throw new Error("No hay objetivo de intercambio.");
      } else {
        try {
          const response = await fetch(
            `http://127.0.0.1:8000/partidas/${matchInfo.id}/jugadores/${userInfo.id}/intercambiar`,
            {
              method: "PATCH",
              body: JSON.stringify({
                id_carta: cardID,
                id_jugador_objetivo: targetExchangeID,
              }),
              headers: {
                "Content-Type": "application/json",
              },
            }
          );

          if (!response.ok)
            throw new Error("Algo salió mal. Intenta de nuevo más tarde");
        } catch (error) {
          console.error(error);
          setCardIsNotValid(true);
        }
      }
    } else if (userInfo.id !== playerTurnID) {
      try {
        const response = await fetch(
          `http://127.0.0.1:8000/partidas/${matchInfo.id}/jugadores/${userInfo.id}/resolver_intercambio`,
          {
            method: "PATCH",
            body: JSON.stringify({
              id_carta: cardID,
            }),
            headers: {
              "Content-Type": "application/json",
            },
          }
        );

        if (!response.ok)
          throw new Error("Algo salió mal. Intenta de nuevo más tarde");
      } catch (error) {
        console.error(error);
        setCardIsNotValid(true);
      }
    }
  }

  const playCard = useCallback(
    async (cardID) => {
      try {
        if (!targetID && targetID !== 0)
          throw new Error("No hay objetivo jugar");
        const response = await fetch(
          `http://127.0.0.1:8000/partidas/${matchInfo.id}/jugadores/${userInfo.id}/jugar`,
          {
            method: "PUT",
            body: JSON.stringify({
              id_carta: cardID,
              id_objetivo: targetID,
            }),
            headers: {
              "Content-Type": "application/json",
            },
          }
        );
        if (!response.ok)
          throw new Error("Algo salió mal. Intenta de nuevo más tarde");
      } catch (error) {
        setCardIsNotValid(true);
        console.error(error);
      }
    },
    [targetID]
  );

  const defend = useCallback(async (cardID) => {
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/partidas/${matchInfo.id}/jugadores/${userInfo.id}/defensa`,
        {
          method: "PUT",
          body: JSON.stringify({
            id_carta: cardID,
          }),
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
      if (!response.ok)
        throw new Error("Algo salió mal. Intenta de nuevo más tarde");

      if (cardID !== -1) {
        const response = await fetch(
          `http://127.0.0.1:8000/partidas/${matchInfo.id}/mazo/robar`,
          {
            method: "PATCH",
            body: JSON.stringify({
              id_jugador: userInfo.id,
              robo_inicio_turno: false,
            }),
            headers: {
              "Content-Type": "application/json",
            },
          }
        );
        if (!response.ok) throw new Error("Algo salio mal...");
      }

      setShowDefenseButtons(false);
    } catch (error) {
      setCardIsNotValid(true);
      console.error(error);
    }
  }, []);

  const defendExchange = useCallback(async (cardID) => {
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/partidas/${matchInfo.id}/jugadores/${userInfo.id}/defensa_intercambio`,
        {
          method: "PUT",
          body: JSON.stringify({
            id_carta: cardID,
          }),
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
      if (!response.ok)
        throw new Error("Algo salió mal. Intenta de nuevo más tarde");

      if (cardID !== -1) {
        const response = await fetch(
          `http://127.0.0.1:8000/partidas/${matchInfo.id}/mazo/robar`,
          {
            method: "PATCH",
            body: JSON.stringify({
              id_jugador: userInfo.id,
              robo_inicio_turno: false,
            }),
            headers: {
              "Content-Type": "application/json",
            },
          }
        );
        if (!response.ok) throw new Error("Algo salio mal...");
      }
      setShowDefenseButtons(false);
    } catch (error) {
      setCardIsNotValid(true);
      console.error(error);
    }
  }, []);

  const buttonStyle = {
    bgColor: "bg-black",
    textColor: "text-white",
  };

  useEffect(() => {
    eventSource.addEventListener("Mano", (event) => {
      const data = JSON.parse(event.data);
      setCardsInHand(data.cartas);
      setContext(data.context);
      setRole(data.rol_jugador);
      setSelectedCardData(null);
      if (data.context === "Defensas") setShowDefenseButtons(true);
    });
  }, []);

  useEffect(() => {
    if (selectedCardData && selectedCardData.target === "self") {
      setTargetID(userInfo.id);
    } else {
      setTargetID(null);
    }
  }, [selectedCardData]);

  return (
    <div className="absolute bottom-14">
      {cardIsNotValid ? (
        <div className="absolute bg-black/90 border-2 -bottom-12 left-96 items-center justify-center flex gap-4 px-2 py-2 border-red-500">
          <h2 className="text-red-500 font-bold"> No puedes usar esa carta de ese modo </h2>
          <Button
            text="Cerrar"
            handleClick={() => setCardIsNotValid(false)}
            textColor={"text-black"}
            bgColor={"bg-red-500"}
          />
        </div>
      ) : null}
      <ul className="flex justify-center w-screen mb-6 gap-2">
        {cardsInHand.map((cardData) => (
          <li key={cardData.id}>
            <SelectableCard
              cardData={cardData}
              isSelected={
                selectedCardData && cardData.id === selectedCardData.id
              }
              setSelectedCardData={setSelectedCardData}
              handContext={context}
            />
          </li>
        ))}
      </ul>
      <div className="flex justify-center w-screen gap-10">
        {selectedCardData &&
          selectedCardData.isPlayable &&
          context !== "Intercambiables" &&
          context !== "Intercambiables_defensa" &&
          !showDefenseButtons && (
            <Button
              text="Jugar"
              handleClick={() => playCard(selectedCardData.id)}
              {...buttonStyle}
            />
          )}
        {selectedCardData &&
          selectedCardData.isDisposable &&
          context !== "Intercambiables" &&
          context !== "Intercambiables_defensa" && (
            <Button
              text="Descartar"
              handleClick={() => disposeCard(selectedCardData.id)}
              {...buttonStyle}
            />
          )}
        {selectedCardData &&
          (context === "Intercambiables" ||
            context === "Intercambiables_defensa" ||
            context === "Vuelta_y_vuelta") && (
            <Button
              text="Intercambiar"
              handleClick={() => exchangeCard(selectedCardData.id)}
              {...buttonStyle}
            />
          )}
        {selectedCardData &&
          context !== "Defensas" &&
          context === "Intercambiables_defensa" &&
          selectedCardData.isPlayable && (
            <Button
              text="Defenderme"
              handleClick={() => defendExchange(selectedCardData.id)}
              {...buttonStyle}
            />
          )}
        {selectedCardData &&
          context === "Defensas" &&
          context !== "Intercambiables" &&
          context !== "Intercambiables_defensa" && (
            <Button
              text="Defenderme"
              handleClick={() => defend(selectedCardData.id)}
              {...buttonStyle}
            />
          )}
        {context === "Defensas" &&
          context !== "Intercambiables" &&
          context !== "Intercambiables_defensa" &&
          showDefenseButtons && (
            <Button
              text="Recibir ataque"
              handleClick={() => defend(-1)}
              {...buttonStyle}
            />
          )}
      </div>
    </div>
  );
};

export default HandOfCards;
