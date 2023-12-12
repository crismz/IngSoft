import sys
sys.path.append("../..")
from fastapi import FastAPI, HTTPException
from sse_starlette import EventSourceResponse

from partidas.schema import Partida, ListaPartida
from partidas.jugadores.schema import Jugador
from partidas.jugadores.utils import event_sender
from utils import WelcomeMessage


lista_jugadores = []

lista_jugadores.append(Jugador(id=0, nombre="C. Auguste Dupin", posicion=0, rol="Human"))
lista_jugadores.append(Jugador(id=1, nombre="Sherlock Holmes", posicion=1, rol="Human"))
lista_jugadores.append(Jugador(id=2, nombre="Long John Silver", posicion=2, rol="Human"))
lista_jugadores.append(Jugador(id=3, nombre="Kelsier", posicion=3, rol="Human"))


lista_partidas = ListaPartida()

pocos_jugadores = Partida(id=0, nombre="patito", contraseña="123", num_jugadores=0,
                          max_jugadores=6, min_jugadores=4, posiciones=[],
                          turno=0, mazo=None, jugadores=[], iniciada=True, conexiones={})

for each in range(len(lista_jugadores)):
    jugador = lista_jugadores[each]
    pocos_jugadores.agregar_jugador(jugador)

lista_partidas.append(pocos_jugadores)

app = FastAPI()

@app.get("/partidas/{id_partida}/jugadores/sse/{id_jugador}", status_code=200)
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
            eventoInicial = WelcomeMessage(msg="Hola wachin")
            current_partida.post_event(id_jugador, eventoInicial)
        return EventSourceResponse(event_sender(current_partida, id_jugador))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

@app.post("/partidas/{id_partida}/jugadores/{id_jugador}/send_events", status_code=200)
async def queue_events(id_partida: int, id_jugador: int):
    evento_intercambio =  WelcomeMessage(msg="Palante")
    evento_mensaje = WelcomeMessage(msg="Patrá")
    evento_rip = WelcomeMessage(msg="Rest in Piss")

    index = lista_partidas.get_index_by_id(id_param=id_partida)
    current_partida = lista_partidas.get_partida_by_index(index)
    current_partida.post_event(id_jugador=id_jugador, event=evento_intercambio)
    current_partida.post_event(id_jugador=id_jugador, event=evento_mensaje)

    current_partida.post_event(id_jugador=id_jugador, event=evento_intercambio)
    current_partida.post_event(id_jugador=id_jugador, event=evento_mensaje)
    
    current_partida.post_event(id_jugador=id_jugador, event=evento_intercambio)
    current_partida.post_event(id_jugador=id_jugador, event=evento_mensaje)
    
    current_partida.post_event(id_jugador=id_jugador, event=evento_intercambio)
    current_partida.post_event(id_jugador=id_jugador, event=evento_mensaje)
    
    current_partida.post_event(id_jugador=id_jugador, event=evento_rip)
