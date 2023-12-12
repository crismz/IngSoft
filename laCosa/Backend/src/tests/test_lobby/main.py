import sys
sys.path.append("../..")
from fastapi import FastAPI, HTTPException
from sse_starlette import EventSourceResponse

from partidas.schema import Partida, ListaPartida, ChatInput, Posicion
from partidas.jugadores.schema import Jugador
from partidas.jugadores.utils import event_sender
from partidas.utils import (
    CHAR_LIMIT_PER_MESSAGE, armador_evento_lobby_jugadores, armar_broadcast,
    armador_evento_log, armador_evento_chat, armador_evento_lobby_iniciada
)
from utils import WelcomeMessage


lista_jugadores = []

lista_jugadores.append(Jugador(id=0, nombre="C. Auguste Dupin", posicion=0, rol="Human"))
lista_jugadores.append(Jugador(id=1, nombre="Sherlock Holmes", posicion=1, rol="Human"))
lista_jugadores.append(Jugador(id=2, nombre="Long John Silver", posicion=2, rol="Human"))
lista_jugadores.append(Jugador(id=3, nombre="Kelsier", posicion=3, rol="Human"))


lista_partidas = ListaPartida()

pocos_jugadores = Partida(id=0, nombre="patito", contraseña="123", num_jugadores=0,
                          max_jugadores=6, min_jugadores=4, posiciones=[],
                          turno=0, mazo=None, jugadores=[], iniciada=False, conexiones={})

for each in range(0,4):
    pocos_jugadores.posiciones.append(Posicion())

lista_partidas.append(pocos_jugadores)

app = FastAPI()


@app.get("/partidas/{id_partida}/jugadores/sse/{id_jugador}/lobby")
async def suscribir_al_lobby(id_partida: int, id_jugador: int):

    # Obtengo la partida deseada mediante el id con {id_partida}
    index = lista_partidas.get_index_by_id(id_param=id_partida)
    if index == -1:
        raise HTTPException(status_code=404, detail=f"Match ID ({id_partida}) Not Found")
    
    # Como la partida existe, la obtenemos
    current_partida = lista_partidas.get_partida_by_index(index)   

    # Chequeamos que la partida esté iniciada
    if current_partida.esta_iniciada():
        raise HTTPException(status_code=422, detail="Game Started Already!")
    
    current_partida.agregar_jugador(lista_jugadores[id_jugador])

    # Chequeamos que el jugador esté en la partida
    if not current_partida.existe_jugador(id_jugador):    
        raise HTTPException(status_code=404, detail=f"Player ID ({id_jugador}) Not Found")
    
    try:
        if not current_partida.is_connected(id_jugador):
            current_partida.connect(id_jugador)
        current_jugadores = current_partida.obtener_jugadores()
        evento_jugadores = armador_evento_lobby_jugadores(current_jugadores)

        # Aunque se broadcastea un evento de jugadores cuando añadimos a cada jugador
        # necesitamos que se envíen estos eventos al jugador que se une
        # por el orden en que se invocan los endpoints
        current_partida.post_event(id_jugador, evento_jugadores, "Lobby_jugadores")
        log = armador_evento_log(
            jugador=current_partida.buscar_jugador(id_jugador),
            context="unirse"
        )
        armar_broadcast(current_partida, log, "Log")
        return EventSourceResponse(event_sender(current_partida, id_jugador))
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@app.post("/partidas/{id_partida}/chat", status_code=200)
async def chatear(id_partida: int, chat_input_data: ChatInput):
    index = lista_partidas.get_index_by_id(id_param=id_partida)
    if index == -1:
        raise HTTPException(status_code=404, detail=f"ID ({id_partida}) Not Found")
    
    _partida_ : Partida = lista_partidas.get_partida_by_index(index)
    
    if len(chat_input_data.mensaje) > CHAR_LIMIT_PER_MESSAGE:
        raise HTTPException(status_code=413, detail="Message Is Too Long")
    
    nombre_emisor = _partida_.buscar_jugador(chat_input_data.id_jugador).get_nombre()
    nuevo_evento_chat = armador_evento_chat(nombre_emisor, chat_input_data.mensaje)

    armar_broadcast(_partida_=_partida_, msg=nuevo_evento_chat, event_name="Chat")

    return
    

@app.delete("/partidas/{id_partida}/jugadores/{id_jugador}/send_events", status_code=200)
async def trigger_death(id_partida: int, id_jugador: int):

    index = lista_partidas.get_index_by_id(id_param=id_partida)
    current_partida = lista_partidas.get_partida_by_index(index)
    
    eliminado = current_partida.buscar_jugador(id_jugador)
    death_message = WelcomeMessage(msg="Die!")
    current_partida.post_event(id_jugador, death_message, "Rest in piss")
    current_partida.eliminar_jugador(eliminado)
    current_jugadores = current_partida.obtener_jugadores()
    evento_jugadores = armador_evento_lobby_jugadores(current_jugadores)
    armar_broadcast(current_partida, evento_jugadores,"Lobby_jugadores")

@app.patch("/partidas/{id_partida}/jugadores/{id_jugador}/send_events", status_code=200)
async def trigger_match(id_partida: int, id_jugador: int):

    index = lista_partidas.get_index_by_id(id_param=id_partida)
    current_partida = lista_partidas.get_partida_by_index(index)
    current_partida.iniciar()
    evento_iniciada = armador_evento_lobby_iniciada(current_partida.esta_iniciada())
    armar_broadcast(current_partida, evento_iniciada, "Lobby_iniciada")

