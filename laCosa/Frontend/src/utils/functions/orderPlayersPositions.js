function orderPlayersPositions(playersPositionsList, player_id) {
  if (playersPositionsList.length === 0) {
    // si no hay jugadores, entonces devuelve un arreglo vacío.
    return [];
  }

  //busco el jugador actual
  const actualPlayer = playersPositionsList.find(
    (player) => player.id_jugador === player_id
  );

  if (!actualPlayer) {
    console.error("No estás en la partida");
    // si el jugador actual no se encuentra, devolvemos []
    return [];
  }

  const ordered_players = [actualPlayer];

  //aqui se agregan los jugadores que siguen en la ronda al jugador actual
  //puede que haya que cambiar cosas si se invierte la ronda, a menos que se maneje en el back
  for (let i = actualPlayer.posicion + 1; i < playersPositionsList.length; i++) {
    ordered_players.push(
      playersPositionsList.find((player) => player.posicion === i) || {}
    );
  }

  // aqui los jugadores que estan antes que el actual
  for (let i = 0; i < actualPlayer.posicion; i++) {
    ordered_players.push(
      playersPositionsList.find((player) => player.posicion === i) || {}
    );
  }

  return ordered_players;
}

export { orderPlayersPositions };
