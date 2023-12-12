from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pony.orm import db_session

import sys
sys.path.append("../..")

from partidas.schema import Partida
from partidas.utils import lista_partidas, armador_evento_mano, armador_evento_mazo
from partidas.jugadores.schema import Jugador
from partidas.mazo.cartas.models import Card
from partidas.mazo.cartas.utils import populate_with_cards
from partidas.mazo.cartas.db import db
from partidas.mazo.cartas.schema import CardSchema
from partidas.mazo.schema import RoboIn, Mazo


app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db.bind('sqlite',filename="db.sqlite", create_db=True)
db.generate_mapping(create_tables=True)
with db_session:
    if Card.select().count() == 0:
        populate_with_cards()

lista_jugadores = [Jugador(id=0, 
                           nombre="Ironclad", 
                           posicion=0, 
                           rol="Humano",
                           acciones_restantes={"robos": 1, "descartes": 1, "intercambios": 1},
                           mano=[CardSchema(id=1000, 
                                            num_players=5, 
                                            type="Accion", 
                                            name="Placeholder",
                                            effect="",
                                            target="self")])]

partida_base = Partida(id=0, nombre="patito", contraseña="123", num_jugadores=4,
                              max_jugadores=6, min_jugadores=4, posiciones=[],
                              turno=0, mazo=Mazo(), 
                              jugadores=lista_jugadores, iniciada=True, 
                              sentido=True, conexiones={})
partida_base.get_mazo().create_deck(0, 4)
    
lista_partidas.append(partida_base)

@app.patch("/partidas/{id_partida}/mazo/robar", status_code=200)
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
        print("Se rompió acá")
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
        print("Mano: " + str(jugador_robo.get_mano()))
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

    return