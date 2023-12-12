import { useCallback, useContext, useEffect, useMemo, useState } from "react";
import CenteredContainer from "../components/CenteredContainer/CenteredContainer";
import Button from "../components/Button/Button";
import { UserAndMatchContext } from "../utils/context/UserAndMatchProvider";
import useNavigation from "../utils/hooks/useNavigation";
import MessageBox from "../components/MessageBox/MessageBox";

const Lobby = () => {
  const [listOfPlayers, setListOfPlayers] = useState([]);

  const { userInfo, matchInfo, resetUserAndMatchState } =
    useContext(UserAndMatchContext);
  const { redirectToMatch, redirectToHome } = useNavigation();

  const eventSource = useMemo(
    () =>
      new EventSource(
        `http://127.0.0.1:8000/partidas/${matchInfo.id}/jugadores/sse/${userInfo.id}/lobby`
      ),
    []
  );

  const isPossibleToStartMatch = useMemo(() => {
    if (!userInfo.isCreator) return false;

    const totalPlayers = listOfPlayers.length;
    return (
      totalPlayers >= matchInfo.minPlayers &&
      totalPlayers <= matchInfo.maxPlayers
    );
  }, [listOfPlayers.length]);

  const startMatch = useCallback(async () => {
    try {
      if (!userInfo.isCreator)
        throw new Error(
          `No eres el creador y por ende no puedes iniciar la partida.`
        );

      if (!isPossibleToStartMatch)
        throw new Error(
          `La cantidad de jugadores debe estar entre ${matchInfo.minPlayers} y ${matchInfo.maxPlayers}`
        );

      const response = await fetch(
        `http://127.0.0.1:8000/partidas/${matchInfo.id}/iniciar`,
        {
          method: "PATCH",
          body: JSON.stringify({ id_jugador: userInfo.id }),
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      if (!response.ok)
        throw new Error("Ha ocurrido un error al enviar la solicitud");

      redirectToMatch(matchInfo.id);
    } catch (error) {
      window.alert(error);
    }
  }, [listOfPlayers.length]);

  const leaveMatch = useCallback(async () => {
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/partidas/${matchInfo.id}/jugadores/${userInfo.id}`,
        {
          method: "DELETE",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      if (!response.ok)
        throw new Error("Ha ocurrido un error al enviar la solicitud");

      resetUserAndMatchState();

      redirectToHome();
    } catch (error) {
      window.alert(error);
    }
  }, []);

  useEffect(() => {
    eventSource.addEventListener("Lobby_jugadores", (event) => {
      const eventData = JSON.parse(event.data);
      setListOfPlayers(eventData.jugadores);
    });

    eventSource.addEventListener("Lobby_iniciada", () => {
      redirectToMatch(matchInfo.id);
    });

    eventSource.addEventListener("Lobby_abortado", () => {
      leaveMatch();
    });

    return () => {
      eventSource.close();
    };
  }, []);

  return (
    <>
      <CenteredContainer>
        <h1 className="text-4xl mb-3 px-6 font-bold">
          Lobby de {matchInfo.name}
        </h1>
        <hr />
        <h2 className="text-xl text-center font-semibold">Jugadores:</h2>
        <ul className="grid grid-cols-2 list-inside place-items-center">
          {listOfPlayers.map(({ name }, index) => (
            <li className="text-lg" key={index}>
              {name}
            </li>
          ))}
        </ul>
        <p className="text-right">
          Cantidad de jugadores: {listOfPlayers.length}
        </p>
        {userInfo.isCreator && (
          <Button
            text="Empezar"
            bgColor={isPossibleToStartMatch ? "bg-white" : "bg-zinc-600"}
            textColor={isPossibleToStartMatch ? "text-black" : "text-white"}
            handleClick={startMatch}
          />
        )}
        <Button
          text="Abandonar"
          bgColor="bg-white"
          textColor="text-black"
          handleClick={leaveMatch}
        />
      </CenteredContainer>
      <MessageBox eventSource={eventSource} />
    </>
  );
};

export default Lobby;
