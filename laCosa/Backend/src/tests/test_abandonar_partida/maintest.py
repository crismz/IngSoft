from fastapi import FastAPI, HTTPException

import sys
sys.path.append("../..")

from partidas.utils import armar_broadcast, armador_evento_lobby_jugadores, eliminar_partida
from partidas.models import PartidaDB
from partidas.schema import Partida, ListaPartida, Posicion
from partidas.jugadores.schema import Jugador, RespuestaMano
from partidas.mazo.cartas.schema import CardSchema
from partidas.croupier.utils import diccionario_croupier


lista_partidas = ListaPartida()

jugadores = [Jugador(id=0, nombre="pepe", posicion=0, rol="Humano", mano=[CardSchema(id=0,num_players=4, type="a", name="primera1", effect="", target=""), 
                                              CardSchema(id=0,num_players=4, type="a", name="segunda1", effect="", target=""),
                                              CardSchema(id=0,num_players=4, type="a", name="tercera1", effect="", target=""),
                                              CardSchema(id=0,num_players=4, type="a", name="cuarta1", effect="", target="")]),
            Jugador(id=1, nombre="jose", posicion=1, rol="Humano", mano=[CardSchema(id=0,num_players=4, type="a", name="primera2", effect="", target=""), 
                                              CardSchema(id=0,num_players=4, type="a", name="segunda2", effect="", target=""),
                                              CardSchema(id=0,num_players=4, type="a", name="tercera2", effect="", target=""),
                                              CardSchema(id=0,num_players=4, type="a", name="cuarta2", effect="", target="")]),
            Jugador(id=2, nombre="pedro", posicion=2, rol="Humano", mano=[CardSchema(id=0,num_players=4, type="a", name="primera3", effect="", target=""), 
                                              CardSchema(id=0,num_players=4, type="a", name="segunda3", effect="", target=""),
                                              CardSchema(id=0,num_players=4, type="a", name="tercera3", effect="", target=""),
                                              CardSchema(id=0,num_players=4, type="a", name="cuarta3", effect="", target="")]),
            Jugador(id=3, nombre="juan", posicion=3, rol="Humano", mano=[CardSchema(id=0,num_players=4, type="a", name="primera4", effect="", target=""), 
                                              CardSchema(id=0,num_players=4, type="a", name="segunda4", effect="", target=""),
                                              CardSchema(id=0,num_players=4, type="a", name="tercera4", effect="", target=""),
                                              CardSchema(id=0,num_players=4, type="a", name="cuarta4", effect="", target="")])]

partida_finalizada = Partida(id=1, nombre="patito", contraseña="123", num_jugadores=4,
                      max_jugadores=6, min_jugadores=4, posiciones=[Posicion(), Posicion(), Posicion(), Posicion()],
                      turno=0, mazo=None, jugadores=jugadores, iniciada=True, finalizada=True)

partida_no_iniciada = Partida(id=2, nombre="patito2", contraseña="123", num_jugadores=4,
                      max_jugadores=6, min_jugadores=4, posiciones=[Posicion(), Posicion(), Posicion(), Posicion()],
                      turno=0, mazo=None, jugadores=jugadores, iniciada=False, finalizada=False)

partida_no_finalizada = Partida(id=3, nombre="patito3", contraseña="123", num_jugadores=4,
                      max_jugadores=6, min_jugadores=4, posiciones=[Posicion(), Posicion(), Posicion(), Posicion()],
                      turno=0, mazo=None, jugadores=jugadores, iniciada=True, finalizada=False)

lista_partidas.append(partida_finalizada)
lista_partidas.append(partida_no_iniciada)
lista_partidas.append(partida_no_finalizada)

app = FastAPI()

@app.get("/partidas", status_code=200)
async def obtener_partidas():
    return lista_partidas


@app.delete("/partidas/{id_partida}/jugadores/{id_jugador}", status_code=200)
async def abandonar_partida(id_partida: int, id_jugador: int):
    # Obtengo la partida deseada mediante el id con {id_partida}
    index = lista_partidas.get_index_by_id(id_param=id_partida)
    if index == -1:
        raise HTTPException(status_code=404, detail=f"ID ({id_partida}) for match Not Found")

    current_partida = lista_partidas.get_partida_by_index(index)
    
    # Si la partida esta iniciada y no finalizada, no se puede abandonar
    if current_partida.esta_iniciada() and not current_partida.esta_finalizada():
        raise HTTPException(status_code=422, detail="Game already started, can't leave now")

    # Verifico si el jugador existe, en caso de que no arrojo 404
    if not current_partida.existe_jugador(id_jugador):
        raise HTTPException(status_code=404, detail=f"ID ({id_jugador}) for player Not Found")
    
    jugador = current_partida.buscar_jugador(id_jugador)

    # Verifico si es el creador de la partida, y que la partida no haya iniciado 
    if id_jugador == 0 and not current_partida.esta_iniciada():
        # Elimino al usuario
        current_partida.eliminar_jugador(jugador=jugador) 
        # Mando a todos los jugadores evento para que abandonen
        armar_broadcast(_partida_=current_partida, msg={}, event_name="Lobby_abortado")

    # Si se va cualquier otro jugador, no importa que la partida haya iniciado o no,
    # se elimina al jugador
    else:
        current_partida.eliminar_jugador(jugador=jugador)
        # Si la partida no esta iniciada, se manda el evento para que sepan que se fue
        if not current_partida.esta_iniciada():
            evento_lobby = armador_evento_lobby_jugadores(current_partida.get_jugadores())
            armar_broadcast(_partida_=current_partida, msg=evento_lobby, event_name="Lobby_jugadores")
        
    # Si era el ultimo jugador, se elimina la partida
    if current_partida.get_num_jugadores() == 0:
            eliminar_partida(current_partida)
            # Eliminamos el croupier correspondiente
            croupier = diccionario_croupier.get_croupier(id)
            diccionario_croupier.remove(id)
            del croupier

    return
