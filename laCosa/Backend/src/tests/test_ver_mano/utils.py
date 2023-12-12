import sys
sys.path.append("../..")

from partidas.mazo.cartas.schema import CardSchema
from partidas.jugadores.schema import Jugador

def crear_manos(jugador: Jugador):
    jugador.set_mano([CardSchema(id=11,
                                  num_players=4,
                                  type="Contagio",
                                  name="Infectado",
                                  effect="",
                                  target="self"),
                       CardSchema(id=22,
                                  num_players=4,
                                  type="Accion",
                                  name="Lanzallamas",
                                  effect="",
                                  target="neighbour"),
                       CardSchema(id=69,
                                  num_players=4,
                                  type="Defensa",
                                  name="Aterrador",
                                  effect="",
                                  target="self"),
                        CardSchema(id=86,
                                  num_players=4,
                                  type="Obstaculo",
                                  name="Puerta atrancada",
                                  effect="",
                                  target="neighbour")])
    if jugador.get_id() == 0:
            jugador.agregar_carta_mano(CardSchema(id=1,
                                               num_players=1,
                                               type="Contagio",
                                               name="La cosa",
                                               effect="La cosa",
                                               target="self"))

    return