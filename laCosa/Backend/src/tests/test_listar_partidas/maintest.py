from fastapi import FastAPI, HTTPException

from sys import path
path.append("../..")

from partidas.schema import Partida, ListaPartida, Posicion, PartidaOut, ListaPartidaOut
from partidas.jugadores.schema import Jugador, RespuestaMano
from partidas.mazo.cartas.schema import CardSchema


lista_partidas = ListaPartida()

jugadores = [Jugador(id=0, nombre="pepe", posicion=0, rol="Humano", mano=[CardSchema(id=0,num_players=4, type="a", name="primera1", effect="", target="any"), 
                                              CardSchema(id=0,num_players=4, type="a", name="segunda1", effect="", target="any"),
                                              CardSchema(id=0,num_players=4, type="a", name="tercera1", effect="", target="any"),
                                              CardSchema(id=0,num_players=4, type="a", name="cuarta1", effect="", target="any")]),
            Jugador(id=1, nombre="jose", posicion=1, rol="Humano", mano=[CardSchema(id=0,num_players=4, type="a", name="primera2", effect="", target="any"), 
                                              CardSchema(id=0,num_players=4, type="a", name="segunda2", effect="", target="any"),
                                              CardSchema(id=0,num_players=4, type="a", name="tercera2", effect="", target="any"),
                                              CardSchema(id=0,num_players=4, type="a", name="cuarta2", effect="", target="any")]),
            Jugador(id=2, nombre="pedro", posicion=2, rol="Humano", mano=[CardSchema(id=0,num_players=4, type="a", name="primera3", effect="", target="any"), 
                                              CardSchema(id=0,num_players=4, type="a", name="segunda3", effect="", target="any"),
                                              CardSchema(id=0,num_players=4, type="a", name="tercera3", effect="", target="any"),
                                              CardSchema(id=0,num_players=4, type="a", name="cuarta3", effect="", target="any")]),
            Jugador(id=3, nombre="juan", posicion=3, rol="Humano", mano=[CardSchema(id=0,num_players=4, type="a", name="primera4", effect="", target="any"), 
                                              CardSchema(id=0,num_players=4, type="a", name="segunda4", effect="", target="any"),
                                              CardSchema(id=0,num_players=4, type="a", name="tercera4", effect="", target="any"),
                                              CardSchema(id=0,num_players=4, type="a", name="cuarta4", effect="", target="any")])]

partida_iniciada = Partida(id=1, nombre="patito", contraseña="123", num_jugadores=4,
                      max_jugadores=6, min_jugadores=4, posiciones=[Posicion(), Posicion(), Posicion(), Posicion()],
                      turno=0, mazo=None, jugadores=jugadores, iniciada=True)

partida_no_iniciada = Partida(id=2, nombre="patito", contraseña="123", num_jugadores=4,
                      max_jugadores=6, min_jugadores=4, posiciones=[Posicion(), Posicion(), Posicion(), Posicion()],
                      turno=0, mazo=None, jugadores=jugadores, iniciada=False)

partida_no_iniciada2 = Partida(id=3, nombre="patito2", contraseña="123", num_jugadores=4,
                      max_jugadores=6, min_jugadores=4, posiciones=[Posicion(), Posicion(), Posicion(), Posicion()],
                      turno=0, mazo=None, jugadores=jugadores, iniciada=False)

partida_no_iniciada3 = Partida(id=4, nombre="patito3", contraseña="", num_jugadores=4,
                      max_jugadores=6, min_jugadores=4, posiciones=[Posicion(), Posicion(), Posicion(), Posicion()],
                      turno=0, mazo=None, jugadores=jugadores, iniciada=False)

partida_no_iniciada4 = Partida(id=5, nombre="patito4", num_jugadores=6,
                      max_jugadores=12, min_jugadores=4, posiciones=[Posicion(), Posicion(), Posicion(), Posicion()],
                      turno=0, mazo=None, jugadores=jugadores, iniciada=False)

lista_partidas.append(partida_iniciada)
lista_partidas.append(partida_no_iniciada)
lista_partidas.append(partida_no_iniciada2)
lista_partidas.append(partida_no_iniciada3)
lista_partidas.append(partida_no_iniciada4)

app = FastAPI()

@app.get("/partidas", status_code=200)
async def listar_partidas():

    # Creamos listado de partidas
    listado = ListaPartidaOut()

    total_partidas = lista_partidas.get_length()

    # Agregamos las partidas que no estén iniciadas
    for i in range(total_partidas):
        partida = lista_partidas.get_partida_by_index(i)
        if(not partida.esta_iniciada()):
            listado.append(PartidaOut(id_partida=partida.get_id(),
                                    nombre_partida=partida.get_nombre(), 
                                    jugadores_act=partida.get_num_jugadores(),
                                    max_jugadores=partida.get_max_jugadores(),
                                    tiene_contraseña=partida.get_contraseña() is not None))
            
    return listado


