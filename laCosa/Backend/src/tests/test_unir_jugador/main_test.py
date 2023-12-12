from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pony.orm import db_session

import sys
sys.path.append("../..")

from partidas.schema import Partida, ListaPartida, DatosUnion
from partidas.jugadores.schema import Jugador
from partidas.utils import armar_broadcast, armador_evento_lobby_jugadores
from partidas.mazo.cartas.models import Card
from partidas.mazo.cartas.utils import populate_with_cards
from partidas.mazo.cartas.db import db

lista_partidas = ListaPartida()

lista_jugadores = [Jugador(id=0, nombre="Ironclad", posicion=0, rol="Humano", mano=[]),
                   Jugador(id=1, nombre="Silent", posicion=1, rol="Humano", mano=[]),
                   Jugador(id=2, nombre="Defect", posicion=2, rol="Humano", mano=[]),
                   Jugador(id=3, nombre="Watcher", posicion=3, rol="Humano", mano=[]),
                   Jugador(id=4, nombre="Neow", posicion=4, rol="Humano", mano=[])]

partida_base = Partida(id=0, nombre="patito", contraseña="123", num_jugadores=5,
                      max_jugadores=6, min_jugadores=4, posiciones=[],
                      turno=0, mazo=None, jugadores=lista_jugadores, iniciada=False)

partida_iniciada = Partida(id=1, nombre="patito", contraseña="123", num_jugadores=5,
                      max_jugadores=6, min_jugadores=4, posiciones=[],
                      turno=0, mazo=None, jugadores=[], iniciada=True)

partida_llena = Partida(id=2, nombre="patito", contraseña="123", num_jugadores=6,
                      max_jugadores=6, min_jugadores=4, posiciones=[],
                      turno=0, mazo=None, jugadores=[], iniciada=False)

lista_partidas.append(partida_base)
lista_partidas.append(partida_iniciada)
lista_partidas.append(partida_llena)


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


@app.post("/partidas/{id_partida}/unir", status_code=201)
async def unir_jugador(id_partida: int, datosUnion: DatosUnion):
    
    # Obtengo la partida deseada mediante el id con {id_partida}
    index = lista_partidas.get_index_by_id(id_param=id_partida)
    if index == -1:
        raise HTTPException(status_code=404, detail=f"ID ({id_partida}) Not Found")
    
    # Esto es una REFERENCIA a la partida, ergo los cambios se reflejan en el objeto original
    _partida_ : Partida = lista_partidas.get_partida_by_index(index)

    # Verifico si aún no ha iniciado la partida, en cuyo caso arrojo 422 (Bad Entity)
    if _partida_.esta_iniciada():
        raise HTTPException(status_code=422, detail="Game Already Started")

    # Guardo el número de jugadores en la partida para usar de acá en adelante
    cantidad_jugadores = _partida_.get_num_jugadores()

    # Veo si hay lugar en la partida. De no ser así, devuelvo 400 (Bad Request)
    if _partida_.get_max_jugadores() == cantidad_jugadores:
        raise HTTPException(status_code=400, detail="Lobby Already at Capacity")

    # Si contraseña != None, comparo contraseñas
    if _partida_.get_contraseña() is not None:
        if _partida_.get_contraseña() != datosUnion.contraseña:
            # Si la contraseña no es correcta, devuelvo 400 (Bad Request)
            raise HTTPException(status_code=400, detail="Incorrect Password")
        
    # Asigno ID al jugador y actualizo la cantidad de jugadores en la partida
    # Busco id de jugador disponible
    for i in range(cantidad_jugadores+1):
        if not _partida_.existe_jugador(i):
            id_jugador = i
            break
        
    nuevo_jugador = Jugador(id=id_jugador, 
                            nombre=datosUnion.nombre_jugador,
                            posicion=id_jugador, 
                            rol="Humano", 
                            mano=[])
    _partida_.agregar_jugador(nuevo_jugador)

    #Broadcasteamos la llegada del nuevo jugador
    evento_jugadores = armador_evento_lobby_jugadores(
        lista_jugadores=_partida_.obtener_jugadores()
    )
    armar_broadcast(_partida_, evento_jugadores, "Lobby_jugadores")
    
    # Incluyo ese mismo ID en la respuesta
    return {"id_jugador" : id_jugador}