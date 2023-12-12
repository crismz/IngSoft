from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pony.orm import db_session

import sys
sys.path.append("../..")

from partidas.mazo.cartas.models import Card
from partidas.mazo.cartas.utils import populate_with_cards
from partidas.mazo.cartas.db import db
from partidas.mazo.cartas.schema import CardSchema
from partidas.mazo.schema import Mazo
from partidas.schema import Partida, ListaPartida
from partidas.jugadores.schema import Jugador
from partidas.croupier.schema import Croupier
from partidas.croupier.utils import DiccionarioCroupier

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

mano : list[CardSchema] = [CardSchema(id=1,num_players=4, type="a", name="carta1", effect="", target="self"),
                            CardSchema(id=2,num_players=4, type="a", name="carta2", effect="", target="any"),
                            CardSchema(id=3,num_players=4, type="a", name="carta3", effect="", target="self"),
                            CardSchema(id=4,num_players=4, type="a", name="carta4", effect="", target="self"),]

mazo : Mazo = Mazo()
mazo.create_deck(0, 5)

lista_jugadores = [Jugador(id=0, nombre="player_0", mano=mano.copy()), 
                   Jugador(id=1, nombre="player_1", mano=mano.copy()), 
                   Jugador(id=2, nombre="player_2", mano=mano.copy()),
                   Jugador(id=3, nombre="player_3", mano=mano.copy()),
                   Jugador(id=4, nombre="player_4", mano=mano.copy())]

partida_no_iniciada = Partida(id=0, nombre="patito", contraseña="123", num_jugadores=5,
                              max_jugadores=6, min_jugadores=4, posiciones=[],
                              turno=0, mazo=mazo, jugadores=lista_jugadores, iniciada=False, sentido=True)

partida_iniciada = Partida(id=1, nombre="patito", contraseña="123", num_jugadores=5,
                           max_jugadores=6, min_jugadores=4, posiciones=[],
                           turno=0, mazo=mazo, jugadores=lista_jugadores, iniciada=True, sentido=True)

lista_partidas : ListaPartida = ListaPartida()
diccionario_croupier : DiccionarioCroupier = DiccionarioCroupier()

lista_partidas.append(partida_no_iniciada)
lista_partidas.append(partida_iniciada)

diccionario_croupier.append(partida=partida_iniciada)
diccionario_croupier.append(partida=partida_no_iniciada)

@app.patch("/partidas/{id_partida}/jugadores/{id_jugador}/descartar", status_code=200)
async def descartar_carta(id_partida: int, id_jugador: int, id_carta: int):
    
    index : int = lista_partidas.get_index_by_id(id_partida)
    if index == -1:
        raise HTTPException(status_code=404, detail=f"ID ({id_partida}) for match Not Found")
    
    _partida_ = lista_partidas.get_partida_by_index(index)
    print(index)
    if not _partida_.esta_iniciada():
        raise HTTPException(status_code=422, detail="Game Not Started Yet")

    # Chequeamos que el jugador esté en la partida
    if not _partida_.existe_jugador(id_jugador):    
        raise HTTPException(status_code=404, detail=f"Player ID ({id_jugador}) Not Found")
    
    # Chequeamos que la carta esté en la mano del jugador
    mano = _partida_.buscar_jugador(id_jugador).get_mano()
    exists : bool = id_carta in [card.get_id() for card in mano]    

    if not exists:
        raise HTTPException(status_code=404, detail=f"Card ID ({id_carta}) Not Found in Player({id_jugador})'s Hand")
    
    # Descartamos la carta
    croupier : Croupier = diccionario_croupier.get_croupier(_partida_.get_id())
    croupier.descartar(id_carta=id_carta, id_jugador=id_jugador)

    # Encolar evento
    #_partida_.broadcast("")
    print(_partida_.jugadores[id_jugador].mano)
    return {"message" : "OK"}