import sys
sys.path.append("../..")
from fastapi import FastAPI, HTTPException
from pony.orm import db_session
from partidas.schema import Partida, ListaPartida
from partidas.mazo.schema import Mazo
from partidas.mazo.cartas.models import Card
from partidas.mazo.cartas.utils import populate_with_cards
from partidas.mazo.cartas.db import db

db.bind('sqlite',filename="db-test.sqlite", create_db=True)
db.generate_mapping(create_tables=True)
with db_session:
    if Card.select().count() == 0:
        populate_with_cards()

lista_partidas = ListaPartida()

partida_iniciada= Partida(id=1, nombre="Partida_1", contraseña=None, num_jugadores=12,
                          max_jugadores=12, min_jugadores=4, posiciones=[],
                          turno=0, mazo=None, jugadores=[], iniciada=True)

partida_no_iniciada = Partida(id=2, nombre="Partida_2", contraseña=None, num_jugadores=12,
                           max_jugadores=12, min_jugadores=4, posiciones=[],
                           turno=0, mazo=None, jugadores=[], iniciada=False)

partida_iniciada_sin_mazo = Partida(id=3, nombre="Partida_3", contraseña=None, num_jugadores=12,
                           max_jugadores=12, min_jugadores=4, posiciones=[],
                           turno=0, mazo=None, jugadores=[], iniciada=True)

partida_iniciada.mazo = Mazo()
partida_iniciada.mazo.create_deck(1, 12)

lista_partidas.append(partida_iniciada)
lista_partidas.append(partida_no_iniciada)
lista_partidas.append(partida_iniciada_sin_mazo)

app = FastAPI()

@app.get("/partidas/{id_partida}/mazo/ver", status_code=200)
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

    is_panic : bool = game.get_mazo().get_first_card_type() == "Panico"
    return {"is_panic" : is_panic}