from fastapi import APIRouter, HTTPException
from partidas.schema import Partida
from partidas.utils import (lista_partidas, armador_evento_mano, get_vecinos, armador_evento_mazo,
                                armador_evento_mostrar_mano, armador_evento_mostrar_cartas)
from partidas.jugadores.schema import Jugador
from partidas.mazo.cartas.schema import CardSchema
from partidas.mazo.schema import Mazo, RoboIn


mazo = APIRouter()

""" Deprecado (Confirmar)
@mazo.get("/ver", status_code=200)
async def get_first_card(id_partida: int): 

    index : int = lista_partidas.get_index_by_id(id_partida)
    if index == -1:
        raise HTTPException(status_code=404, detail=f"ID ({id_partida}) Not Found")    
    # Si el index no es -1 entonces la partida deberia existir
    game : Partida = lista_partidas.get_partida_by_index(index)

    if not lista_partidas.get_partida_by_index(index).esta_iniciada():
        raise HTTPException(status_code=422, detail="Game Not Yet Started")

    if game.mazo is None:
        raise HTTPException(status_code=404, detail="Deck not created")

    is_panic : bool = game.get_mazo().get_first_card_type() == "¡Panico!"

    game.broadcast(armador_evento_mano(game), "Mazo")

    return {"is_panic" : is_panic}
"""
    
@mazo.patch("/robar", status_code=200)
async def robar_carta(id_partida: int, data_in: RoboIn):
    index : int = lista_partidas.get_index_by_id(id_partida)
    if index == -1:
        raise HTTPException(status_code=404, detail=f"Partida ID ({id_partida}) Not Found")
    
    _partida_ : Partida = lista_partidas.get_partida_by_index(index)
    if not _partida_.esta_iniciada():
        raise HTTPException(status_code=422, detail="Game Not Yet Started")
    
    jugador_id : int = data_in.id_jugador
    if  _partida_.buscar_jugador(jugador_id) == None:
        raise HTTPException(status_code=404, detail=f"Jugador ID ({jugador_id}) Not Found")

    _mazo_ : Mazo = _partida_.get_mazo()
    if _mazo_ is None:
        raise HTTPException(status_code=422, detail=f"Partida ID ({id_partida}) Has No Deck")
    
    jugador_robo : Jugador = _partida_.buscar_jugador(jugador_id)
    carta_robada: CardSchema

    if not data_in.robo_inicio_turno:
        while jugador_robo.quedan_acciones("robos"):
            carta_robada = _mazo_.take_card()
            while carta_robada.get_type() == "Panico":
                _mazo_.discard_card(carta_robada)
                carta_robada = _mazo_.take_card()
            jugador_robo.agregar_carta_mano(carta_robada)
            jugador_robo.restar_accion("robos")
    else:
        carta_robada = _mazo_.take_card()
        jugador_robo.agregar_carta_mano(carta_robada)
        jugador_robo.restar_accion("robos")

    evento_mazo_nuevo = armador_evento_mazo(_partida_)

    _partida_.broadcast(msg=evento_mazo_nuevo, event_name="Mazo")

    if data_in.robo_inicio_turno:
        evento_respuesta = armador_evento_mano(jugador=jugador_robo, 
                                               instancia="Jugar_Descartar", 
                                               context="Robo")
    else:
        evento_respuesta = armador_evento_mano(jugador=jugador_robo, 
                                               instancia="Esperar", 
                                               context="Esperando")

    _partida_.post_event(id_jugador=jugador_id, event=evento_respuesta, event_name="Mano")
    if jugador_robo.esta_en_cuarentena():
        cards = [armador_evento_mostrar_cartas(
            carta_robada.get_id(), carta_robada.get_name(),
            carta_robada.get_type(), carta_robada.get_effect()
        )]
        _partida_.broadcast(
            msg=armador_evento_mostrar_mano(jugador_robo.get_id(), cards),
            event_name="Cartas_mostrables"
            )
    return