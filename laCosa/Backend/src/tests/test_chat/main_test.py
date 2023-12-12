from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pony.orm import db_session
from sse_starlette import EventSourceResponse
from pydantic import BaseModel

import sys
sys.path.append("../..")

from partidas.schema import Partida, ListaPartida, ChatInput
from partidas.utils import armar_broadcast, armador_evento_chat, CHAR_LIMIT_PER_MESSAGE
from partidas.jugadores.schema import Jugador
from partidas.jugadores.utils import event_sender
from partidas.mazo.cartas.models import Card
from partidas.mazo.cartas.utils import populate_with_cards
from partidas.mazo.cartas.db import db


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

lista_jugadores = [Jugador(id=0, nombre="Ironclad", posicion=0, rol="La Cosa", mano=[]), 
                   Jugador(id=1, nombre="Silent", posicion=1, rol="Humano", mano=[]),
                   Jugador(id=2, nombre="Defect", posicion=2, rol="Infectado", mano=[])]

partida_ejemplo = Partida(id=0, nombre="patito", contraseña="123", num_jugadores=3,
                              max_jugadores=3, min_jugadores=3, posiciones=[],
                              turno=0, mazo=None, jugadores=lista_jugadores, 
                              iniciada=True, sentido=True, conexiones={})

lista_partidas = ListaPartida(lista=[partida_ejemplo])

class WelcomeMessage(BaseModel):
    msg: str = ""

@app.get("/")
async def hub():
    return {"message" : "Main Hub"}

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
    

@app.post("/partidas/{id_partida}/chat", status_code=200)
async def chatear(id_partida: int, chat_input_data: ChatInput):
    index = lista_partidas.get_index_by_id(id_param=id_partida)
    if index == -1:
        raise HTTPException(status_code=404, detail=f"ID ({id_partida}) Not Found")
    
    _partida_ : Partida = lista_partidas.get_partida_by_index(index)

    if not _partida_.esta_iniciada():
        print(_partida_.iniciada)
        raise HTTPException(status_code=422, detail="Game Not Yet Started")
    
    if len(chat_input_data.mensaje) > CHAR_LIMIT_PER_MESSAGE:
        raise HTTPException(status_code=413, detail="Message Is Too Long")
    
    nombre_emisor = _partida_.buscar_jugador(chat_input_data.id_jugador).get_nombre()
    nuevo_evento_chat = armador_evento_chat(nombre_emisor, chat_input_data.mensaje)

    armar_broadcast(_partida_=_partida_, msg=nuevo_evento_chat, event_name="Chat")

    return