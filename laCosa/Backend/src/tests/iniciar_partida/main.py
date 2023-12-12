from fastapi import FastAPI, HTTPException
import sys
sys.path.append("../..")
from partidas.schema import Partida, ListaPartida, DatosInicio, Posicion
from partidas.utils import primer_turno, repartir_cartas, armador_evento_lobby_iniciada, armar_broadcast
from partidas.mazo.schema import Mazo
from pony.orm import db_session
from partidas.models import PartidaDB
from partidas.croupier.schema import DiccionarioCroupier
from partidas.mazo.cartas.models import Card
from partidas.mazo.cartas.db import db
from partidas.mazo.cartas.utils import populate_with_cards

db.bind('sqlite',filename="db.sqlite", create_db=True)
db.generate_mapping(create_tables=True)
with db_session:
    if Card.select().count() == 0:
        populate_with_cards()

lista_partidas = ListaPartida()

pocos_jugadores = Partida(id=0, nombre="patito", contraseña="123", num_jugadores=3,
                          max_jugadores=6, min_jugadores=4, posiciones=[],
                          turno=0, mazo=None, jugadores=[], iniciada=False)

partida_iniciada = Partida(id=1, nombre="patito", contraseña="123", num_jugadores=5,
                           max_jugadores=6, min_jugadores=4, posiciones=[],
                           turno=0, mazo=None, jugadores=[], iniciada=True)

partida_valida = Partida(id=2, nombre="patito", contraseña="123", num_jugadores=5,
                         max_jugadores=6, min_jugadores=4, posiciones=[],
                         turno=0, mazo=Mazo(id_partida=2), jugadores=[], iniciada=False)

lista_partidas.append(pocos_jugadores)
lista_partidas.append(partida_iniciada)
lista_partidas.append(partida_valida)

app = FastAPI()

diccionario_croupier = DiccionarioCroupier()

@app.patch("/{id_partida}/iniciar", status_code=200)
async def iniciar_partida(id_partida: int, datosInicio: DatosInicio):

    id_jugador = datosInicio.id_jugador
    # Chequeamos si la partida está creada
    index = lista_partidas.get_index_by_id(id_partida)
    if index == -1:
        raise HTTPException(status_code=404, detail=f"ID ({id_partida}) Not Found")
    
    # Chequeamos si el jugador que inicia la partida es el creador
    if id_jugador != 0:
        raise HTTPException(status_code=422, detail=f"ID ({id_jugador}) Is Invalid")
    
    # Chequeamos que haya suficientes jugadores
    current_partida = lista_partidas.get_partida_by_index(index)
    jugadores_unidos = current_partida.get_num_jugadores()
    jugadores_requeridos = current_partida.get_min_jugadores()
    if jugadores_unidos < jugadores_requeridos:
        raise HTTPException(status_code=400, detail=f"Not Enough Players")
    
    # Chequeamos si la partida ya está iniciada
    if current_partida.esta_iniciada():
        raise HTTPException(status_code=422, detail="Game Already Started")
    
    # Creamos el mazo
    current_mazo = current_partida.get_mazo()
    current_mazo.create_deck(id_partida, jugadores_unidos)

    # Creamos las posiciones
    for each in range(jugadores_unidos):
        current_partida.agregar_posicion(Posicion())

    # Asignamos el primer turno
    current_partida.set_turno(primer_turno(jugadores_unidos))

    # Asignamos los jugadores que hay al iniciar la partida
    current_partida.set_num_jugadores_inicial(jugadores_unidos)

    # Repartimos las cartas
    repartir_cartas(mazo=current_mazo, jugadores=current_partida.obtener_jugadores())

    # Cambiar el estado de la partida a iniciada en database
    with db_session:
        entidad_partida = PartidaDB.get(partida_id=current_partida.get_id())
        if entidad_partida:
            entidad_partida.iniciada = True

    # Cambiar el estado de la partida a iniciada en el back
    current_partida.iniciar()

    # Agregamos un croupier al diccionario de croupiers
    diccionario_croupier.append(current_partida) 

    # Hacemos la respuesta para el front
    response = {"message" : "ok"}

    #Broadcasteamos que la partida está iniciada
    evento_iniciada = armador_evento_lobby_iniciada(current_partida.esta_iniciada())
    armar_broadcast(current_partida, evento_iniciada, "Lobby_iniciada")

    return response