from partidas.schema import Partida
from partidas.mazo.schema import Mazo
from partidas.mazo.cartas.schema import CardSchema
from partidas.jugadores.schema import Jugador
from typing import List
from sse_starlette import ServerSentEvent
import asyncio
import json

async def event_sender(_partida_: Partida, id_jugador: int):
    try:
        while True:
            if _partida_.is_connected(id_jugador) and _partida_.has_events(id_jugador):
                tupla_evento = _partida_.get_event(id_jugador)
                response = ServerSentEvent(data=json.dumps(tupla_evento[0].dict()), event=tupla_evento[1])
                yield response
            await asyncio.sleep(0.25)
    except asyncio.CancelledError:
        print(f"El jugador {id_jugador} metió el router al microondas")
    except Exception as e:
        print(f"Hubo problemas con el jugador {id_jugador}: {e}")


# Obtener el id del jugador para el intercambio y volver a setearlo a -1 al terminar
def obtener_objetivo_intercambio(partida: Partida, jugador: Jugador):
    id_guardado: int = jugador.get_id_objetivo_intercambio()
    # Si no es -1, una carta cambió el objetivo del intercambio
    if id_guardado != -1:
        return id_guardado
    # Si es -1, calculamos el siguente en la ronda
    posicion_actual: int = jugador.get_posicion()
    sentido_incremental: bool = partida.get_sentido()
    # Reminder: sentido = True significa sentido incremental de las posiciones; False lo contrario
    if sentido_incremental:
        if posicion_actual == (partida.get_num_jugadores() - 1):
            id_guardado = (partida.buscar_jugador_por_posicion(0)).get_id()
        else:
            id_guardado = (partida.buscar_jugador_por_posicion(posicion_actual + 1)).get_id()
    else:
        if posicion_actual == 0:
            id_guardado = (partida.buscar_jugador_por_posicion(partida.get_num_jugadores() - 1)).get_id()
        else:
            id_guardado = (partida.buscar_jugador_por_posicion(posicion_actual - 1)).get_id()

    return id_guardado

# Valido el caso borde -no tan borde- del intercambio
def verificar_intercambio(jugador_emisor: Jugador, rol_receptor: str, id_carta: CardSchema):
    carta_en_cuestion: CardSchema = jugador_emisor.obtener_carta(id_carta=id_carta)
    if carta_en_cuestion is None:
        return False
    if jugador_emisor.get_rol() == "Infectado" and carta_en_cuestion.get_type() == "Contagio":
        if not rol_receptor == "La Cosa":
            return False
    return True

# También se encarga de infectar a un jugador si se dan las condiciones para hacerlo
def intercambiar_cartas(ids_cartas: List[int], jugadores: List[Jugador]):
    cartas: List[CardSchema] = []
    cartas.append(jugadores[0].remover_carta_mano(id_carta=ids_cartas[0]))
    cartas.append(jugadores[1].remover_carta_mano(id_carta=ids_cartas[1]))

    jugadores[0].agregar_carta_mano(cartas[1])
    jugadores[1].agregar_carta_mano(cartas[0])

    if (jugadores[0].get_rol() == "La Cosa" and 
        cartas[0].get_name() == "Infectado" and
        not jugadores[1].get_inmunidad()):
        jugadores[1].set_rol(rol="Infectado")

    elif (jugadores[1].get_rol() == "La Cosa" and 
          cartas[1].get_name() == "Infectado" and
          not jugadores[0].get_inmunidad()):
        jugadores[0].set_rol(rol="Infectado")

    cartas.clear()
    return

def intercambiar_con_mazo(id_carta: int, jugador: Jugador, partida: Partida):
    carta_jugador : CardSchema = jugador.remover_carta_mano(id_carta)
    mazo: Mazo = partida.get_mazo()
    carta_nueva: CardSchema = mazo.take_card()
    while carta_nueva.get_type() == "Panico":
        mazo.discard_card(carta_nueva)
        carta_nueva = mazo.take_card()
    jugador.agregar_carta_mano(carta_nueva)
    mazo.place_on_top(carta_jugador)
    return