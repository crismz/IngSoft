from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pony.orm import db_session
from sse_starlette import EventSourceResponse
from pydantic import BaseModel

import sys
sys.path.append("../..")

from partidas.schema import Partida
from partidas.utils import (lista_partidas, armador_evento_turno, repartir_cartas,
                            armar_broadcast)
from partidas.jugadores.schema import Jugador
from partidas.jugadores.utils import event_sender
from partidas.mazo.cartas.models import Card
from partidas.mazo.cartas.utils import populate_with_cards
from partidas.mazo.cartas.db import db
from partidas.mazo.schema import Mazo


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

lista_jugadores = [Jugador(id=0, nombre="Ironclad", posicion=0, rol="Humano"), 
                   Jugador(id=1, nombre="Silent", posicion=1, rol="Humano"), 
                   Jugador(id=2, nombre="Defect", posicion=2, rol="Humano"),
                   Jugador(id=3, nombre="Watcher", posicion=3, rol="Humano"),
                   Jugador(id=4, nombre="Neow", posicion=4, rol="Humano")]

partida = Partida(id=2, nombre="patito", contraseña="123", num_jugadores=5,
                              max_jugadores=6, min_jugadores=4, posiciones=[],
                              turno=0, mazo=None, jugadores=lista_jugadores, 
                              iniciada=True, sentido=True, conexiones={})
partida.set_mazo(Mazo(id_partida=2))
partida.get_mazo().create_deck(2, 5)
repartir_cartas(partida.get_mazo(), partida.obtener_jugadores())


lista_partidas.append(partida)

@app.get("/partidas/{id_partida}/jugadores/sse/{id_jugador}")
async def suscribir_al_stream(id_partida: int, id_jugador: int):

    # Obtengo la partida deseada mediante el id con {id_partida}
    index = lista_partidas.get_index_by_id(id_param=id_partida)
    if index == -1:
        raise HTTPException(status_code=404, detail=f"Match ID ({id_partida}) Not Found")
    
    # Como la partida existe, la obtenemos
    current_partida = lista_partidas.get_partida_by_index(index)   

    # Chequeamos que la partida esté iniciada
    if not current_partida.esta_iniciada():
        raise HTTPException(status_code=422, detail="Game Not Started Yet")

    # Chequeamos que el jugador esté en la partida
    if not current_partida.existe_jugador(id_jugador):    
        raise HTTPException(status_code=404, detail=f"Player ID ({id_jugador}) Not Found")
    
    try:
        if not current_partida.is_connected(id_jugador):
            current_partida.connect(id_jugador)
            # Acá añadimos el evento de "Conexión exitosa" o similar
            #current_partida.post_event(id_jugador, SuccessfulConectionEvent)

            # Agregamos el evento de Ronda, Turno, Mazo y Mano
            # No se hace broadcasting, porque se envia a cada jugador que se conecta
            # por lo tanto lo terminan recibiendo todos
            current_partida.post_event(id_jugador=id_jugador, 
                                       event=armador_evento_turno(id_partida),
                                       event_name="Turno")

        return EventSourceResponse(event_sender(current_partida, id_jugador))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

@app.patch("/partidas/{id_partida}/finalizar_turno", status_code=200)
async def fin_turno(id_partida: int):

    # Obtengo la partida deseada mediante el id con {id_partida}
    index = lista_partidas.get_index_by_id(id_param=id_partida)
    if index == -1:
        raise HTTPException(status_code=404, detail=f"ID ({id_partida}) Not Found")
    
    # Esto es una REFERENCIA a la partida, ergo los cambios se reflejan en el objeto original
    _partida_ : Partida = lista_partidas.get_partida_by_index(index)

    # Verifico si aún no ha iniciado la partida, en cuyo caso arrojo 422 (Bad Entity)
    if not _partida_.esta_iniciada():
        raise HTTPException(status_code=422, detail="Game Not Yet Started")
    
    #  Primero necesito saber cuántos jugadores hay, ya que dados N jugadores presentes
    # en la partida, las posiciones estarán definidas de 0 a N - 1 clockwise
    ultima_posicion : int = _partida_.get_num_jugadores() - 1

    turno_por_terminar : int = _partida_.get_turno()

    proximo_turno : int

    #  Si el sentido es positivo/clockwise (True), sumo 1 al turno salvo que se trate de la ultima
    # posición, en cuyo caso el turno pasa a tenerlo quien se encuentre en la primera posición (0)
    if _partida_.get_sentido() == True:
        if turno_por_terminar == ultima_posicion:
            proximo_turno = 0
        else:
            proximo_turno = turno_por_terminar + 1
    #  Si el sentido es negativo/counter-clockwise (False), sustraigo 1 al turno salvo que se trate de
    # la primera posición, en cuyo caso el turno pasa a tenerlo quien se encuentre en la última posición
    else:
        if turno_por_terminar == 0:
            proximo_turno = ultima_posicion
        else:
            proximo_turno = turno_por_terminar - 1
    
    # Los cambios a 
    _partida_.set_turno(proximo_turno)

    # Enviamos el evento de turno
    armar_broadcast(_partida_,msg=armador_evento_turno(_partida_.get_id()), event_name="Turno")

    # Según el acuerdo del Excel, este endpoint sólo devuelve el código de la operación (200 si sale todo bien)
    return