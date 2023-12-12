import sys
sys.path.append("../../..")
from pony.orm import db_session
from fastapi import FastAPI, HTTPException
from partidas.croupier.schema import Croupier
from partidas.mazo.schema import Mazo
from partidas.mazo.cartas.models import Card
from partidas.mazo.cartas.utils import populate_with_cards
from partidas.mazo.cartas.db import db
from partidas.schema import Partida, ListaPartida, Posicion
from partidas.mazo.cartas.schema import CardSchema
from partidas.jugadores.schema import Jugador

db.bind('sqlite',filename="db-test.sqlite", create_db=True)
db.generate_mapping(create_tables=True)
with db_session:
    if Card.select().count() == 0:
        populate_with_cards()

lista_jugadores = []

lista_jugadores.append(Jugador(id=0, nombre="C. Auguste Dupin", posicion=0, rol="Human"))
lista_jugadores.append(Jugador(id=1, nombre="Sherlock Holmes", posicion=1, rol="Human"))
lista_jugadores.append(Jugador(id=2, nombre="Long John Silver", posicion=2, rol="Human"))
lista_jugadores.append(Jugador(id=3, nombre="Kelsier", posicion=3, rol="Human"))

lista_jugadores_copy = lista_jugadores.copy()

lista_partidas = ListaPartida()

pocos_jugadores = Partida(id=0, nombre="patito", contraseña="123", num_jugadores=0,
                          max_jugadores=6, min_jugadores=4, posiciones=[],
                          turno=0, mazo=None, jugadores=[], iniciada=True)


for each in range(len(lista_jugadores)):
    jugador = lista_jugadores[each]
    lanzallamas = CardSchema(id=22+each,
                             num_players=len(lista_jugadores),
                            type="Acción",
                            name="Lanzallamas",
                            effect="Quemar a un jugador adyacente")
    jugador.agregar_carta_mano(lanzallamas)
    posicion = Posicion()
    if each == 0:
        posicion.bloquear_pos(1)
    elif each == 1:
        posicion.bloquear_pos(0)
        posicion.bloquear_pos(1)
    elif each == 2:
        posicion.bloquear_pos(0)
    pocos_jugadores.agregar_jugador(jugador)
    pocos_jugadores.agregar_posicion(posicion)

mazo = Mazo()
mazo.create_deck(0,4)
pocos_jugadores.set_mazo(mazo)

lista_partidas.append(pocos_jugadores)

croupier = Croupier()

app = FastAPI()

@app.get("/{id_partida}/quemar/{id_jugador}/{id_objetivo}/{id_carta}", status_code=200)
async def listar_jugadores(id_partida: int, id_jugador: int, id_objetivo: int, id_carta: int):

    # Chequeamos si la partida está creada
    index = lista_partidas.get_index_by_id(id_param=id_partida)
    if index == -1:
        raise HTTPException(status_code=404, detail=f"Match ID ({id_partida}) Not Found")
    # Como la partida existe, la obtenemos
    current_partida = lista_partidas.get_partida_by_index(index)
    
    #Verificamos que los jugadores existen
    if not current_partida.existe_jugador(id_jugador):
        raise HTTPException(status_code=404, detail=f"Player ID ({id_jugador}) Not Found")
    if not current_partida.existe_jugador(id_objetivo):
        raise HTTPException(status_code=404, detail=f"Player ID ({id_objetivo}) Not Found")
    
    jugador = current_partida.buscar_jugador(id_jugador)
    mano = jugador.get_mano()
    in_hand = False
    for each in mano:
        in_hand = in_hand or (each.get_id() == id_carta)

    if not in_hand:
        raise HTTPException(status_code=404, detail=f"Card ID ({id_carta}) Not Found")
    
    # Verificamos si el lanzallamas se puede usar
    if croupier.verificar_efecto(id_carta, id_jugador, id_objetivo, current_partida):
        # Hacemos que el croupier le quite la carta de la mano al jugador y la descarte
        croupier.descartar(id_carta, id_jugador, current_partida) 
        # Hacemos que el croupier queme al jugador objetivo
        croupier.aplicar_efecto(id_carta, id_objetivo, current_partida)
    else:
        raise HTTPException(status_code=400, detail=f"Card ID ({id_carta}) Cannot Be Played That Way!")

    # Preparamos la respuesta para el front
    jugadores_unidos = current_partida.obtener_jugadores()
    lista_unidos = []

    for each in jugadores_unidos:
        nombre_jugador = each.get_nombre()

        lista_unidos.append({"name" : nombre_jugador})
    
    response = {
        "jugadores" : lista_unidos
    }
    
    return response