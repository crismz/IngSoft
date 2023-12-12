import HandOfCards from "../components/HandOfCards/HandOfCards.jsx";
import ShowOtherPlayerCards from "../components/ShowOtherPlayerCards/ShowOtherPlayerCards.jsx";
import Deck from "../components/Deck/Deck.jsx";
import ShowCardPlayed from "../components/ShowCardPlayed/ShowCardPlayed.jsx";
import ExchangeForPlayerInTurn from "../components/ExchangeForPlayerInTurn/ExchangeForPlayerInTurn.jsx";
import ShowPlayersPositions from "../components/ShowPlayersPositions/ShowPlayersPositions.jsx";
import { useContext, useEffect, useMemo, useState } from "react";
import { UserAndMatchContext } from "../utils/context/UserAndMatchProvider.jsx";
import MatchEndModal from "../components/MatchEndModal/MatchEndModal.jsx";
import TargetProvider from "../utils/context/TargetProvider.jsx";
import TargetExchangeProvider from "../utils/context/TargetExchangeProvider.jsx";
import EndOfTurnButton from "../components/EndOfTurnButton/EndOfTurnButton.jsx";
import DeathScreen from "../components/DeathScreen/DeathScreen.jsx";
import ExchangeForRequestedPlayer from "../components/ExchangeForRequestedPlayer/ExchangeForRequestedPlayer.jsx";
import MessageBox from "../components/MessageBox/MessageBox.jsx";
import DeclareWinButton from "../components/DeclareWinButton/DeclareWinButton.jsx";
import { RoleProvider } from "../utils/context/RoleProvider.jsx";
import PlayerRole from "../components/PlayerRole/PlayerRole.jsx";
import RevelationCard from "../components/RevelationCard/RevelationCard.jsx";

const Match = () => {
  const [playerTurnID, setPlayerTurnID] = useState(-1);
  const { userInfo, matchInfo } = useContext(UserAndMatchContext);
  const eventSource = useMemo(
    () =>
      new EventSource(
        `http://127.0.0.1:8000/partidas/${matchInfo.id}/jugadores/sse/${userInfo.id}`
      ),
    []
  );

  useEffect(() => {
    eventSource.addEventListener("Turno", (event) => {
      const eventData = JSON.parse(event.data);
      setPlayerTurnID(eventData.id_jugador);
    });
  }, []);

  return (
    <div className="h-screen">
      <MatchEndModal eventSource={eventSource} />
      <DeathScreen eventSource={eventSource} />
      <TargetExchangeProvider>
        <RoleProvider>
          <PlayerRole />
          <TargetProvider>
            <EndOfTurnButton eventSource={eventSource} />
            <DeclareWinButton playerTurnID={playerTurnID} />
            <ExchangeForPlayerInTurn
              eventSource={eventSource}
              playerTurnID={playerTurnID}
            />
            <ExchangeForRequestedPlayer
              eventSource={eventSource}
              playerTurnID={playerTurnID}
            />
            <ShowPlayersPositions
              eventSource={eventSource}
              playerTurnID={playerTurnID}
            />
            <HandOfCards
              eventSource={eventSource}
              playerTurnID={playerTurnID}
            />
          </TargetProvider>
        </RoleProvider>
      </TargetExchangeProvider>
      <div className="absolute m-auto left-0 right-0 top-0 bottom-52 w-fit h-fit flex gap-20">
        <ShowCardPlayed eventSource={eventSource} />
        <Deck eventSource={eventSource} playerTurnID={playerTurnID} />
      </div>
      <MessageBox eventSource={eventSource} />
      <ShowOtherPlayerCards eventSource={eventSource} />
      <RevelationCard eventSource={eventSource} />
    </div>
  );
};

export default Match;
