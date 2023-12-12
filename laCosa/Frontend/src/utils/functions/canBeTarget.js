const canBeTarget = (orderedPlayers, targetPositionInfo, playerID) => {
  if (targetPositionInfo === "neighbour")
    return (
      orderedPlayers.at(-1).id_jugador === playerID ||
      orderedPlayers.at(1).id_jugador === playerID
    );

  if (targetPositionInfo === "self")
    return orderedPlayers[0].id_jugador === playerID;

  if (targetPositionInfo === "direction")
    return (
      orderedPlayers.at(3 % orderedPlayers.length).id_jugador === playerID ||
      orderedPlayers.at(-3 % orderedPlayers.length).id_jugador === playerID
    );

  if (targetPositionInfo === "quarantine_door")
    return (
      (orderedPlayers.at(-1).id_jugador === playerID &&
        orderedPlayers.at(-1).tiene_cuarentena) ||
      (orderedPlayers[0].id_jugador === playerID &&
        orderedPlayers[0].tiene_cuarentena) ||
      (orderedPlayers.at(1).id_jugador === playerID &&
        orderedPlayers.at(1).tiene_cuarentena)
    );

  if (targetPositionInfo === "door")
    return (
      (orderedPlayers.at(-1).id_jugador === playerID &&
        orderedPlayers.at(-1).puerta_atrancada_izq) ||
      (orderedPlayers[0].id_jugador === playerID &&
        orderedPlayers[0].puerta_atrancada_izq)
    );

  if (targetPositionInfo === "any") return true;

  if (targetPositionInfo === "none") return false;

  return false;
};

export default canBeTarget;
