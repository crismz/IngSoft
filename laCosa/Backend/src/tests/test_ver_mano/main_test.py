from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette import EventSourceResponse
from pydantic import BaseModel

import sys
sys.path.append("../..")

from partidas.schema import Partida, Posicion
from partidas.utils import lista_partidas, armador_evento_mano
from partidas.jugadores.schema import Jugador
from partidas.jugadores.utils import event_sender
from partidas.mazo.cartas.models import Card
from partidas.mazo.cartas.db import db
from partidas.mazo.cartas.schema import CardSchema
from partidas.mazo.schema import RoboIn, Mazo

from utils import crear_manos

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
lista_jugadores = [Jugador(id=0, nombre="Ironclad", posicion=0, rol="La Cosa", mano=[]), 
                   Jugador(id=1, nombre="Silent", posicion=1, rol="Humano", mano=[]),
                   Jugador(id=2, nombre="Defect", posicion=2, rol="Infectado", mano=[])]

partida_ejemplo = Partida(id=0, nombre="patito", contraseña="123", num_jugadores=3,
                              max_jugadores=3, min_jugadores=3, 
                              posiciones=[Posicion(), Posicion(), Posicion()],
                              turno=0, mazo=None, jugadores=lista_jugadores, 
                              iniciada=True, sentido=True, conexiones={})

crear_manos(lista_jugadores[0])
crear_manos(lista_jugadores[1])
crear_manos(lista_jugadores[2])

lista_partidas.append(partida_ejemplo)

class WelcomeMessage(BaseModel):
    msg: str = ""


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
            eventoInicial = WelcomeMessage(msg="Greetings, traveller")
            current_partida.post_event(id_jugador, eventoInicial, "Bienvenida")
        return EventSourceResponse(event_sender(current_partida, id_jugador))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

@app.get("/jugadores/{id_jugador}/evaluador_mano/{instancia}", status_code=200)
async def evaluador_mano(id_jugador: int, instancia: str):
    if instancia == "Close":
        partida_ejemplo.post_event(id_jugador, WelcomeMessage(msg="Bye bye"), "Fin")
    jugador = partida_ejemplo.buscar_jugador(id_jugador)
    evento_mano = armador_evento_mano(jugador, instancia, context="Algun contexto de mano")
    partida_ejemplo.post_event(id_jugador, evento_mano, "Mano")
    return