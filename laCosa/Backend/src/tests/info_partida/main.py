from fastapi import FastAPI, HTTPException
import sys
sys.path.append("../..")
from partidas.schema import Partida, ListaPartida, DatosInicio

lista_partidas = ListaPartida()

pocos_jugadores = Partida(id=0, nombre="LasAventurasDelCapitanHatteras", contraseña="123", num_jugadores=3,
                          max_jugadores=4, min_jugadores=4, posiciones=[],
                          turno=0, mazo=None, jugadores=[], iniciada=False)

muchos_jugadores = Partida(id=1, nombre="LaSombraSobreInnsmouth", contraseña="123", num_jugadores=5,
                           max_jugadores=12, min_jugadores=4, posiciones=[],
                           turno=0, mazo=None, jugadores=[], iniciada=True)


lista_partidas.append(pocos_jugadores)
lista_partidas.append(muchos_jugadores)

app = FastAPI()


@app.get("/{id_partida}", status_code=200)
async def info_partida(id_partida: int):
    
    # Chequeamos si la partida está creada
    index = lista_partidas.get_index_by_id(id_partida)
    if index == -1:
        raise HTTPException(status_code=404, detail=f"ID ({id_partida}) Not Found")
    
    # Como la partida está creada, preparamos la respuesta al front
    current_partida = lista_partidas.get_partida_by_index(index)
    response = {
        "nombre_partida" : current_partida.get_nombre(),
        "min_jugadores": current_partida.get_min_jugadores(),
        "max_jugadores": current_partida.get_max_jugadores()
    }

    return response
