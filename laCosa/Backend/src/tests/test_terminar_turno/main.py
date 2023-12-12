from fastapi import FastAPI, HTTPException
import sys
sys.path.append("../..")

from partidas.schema import Partida, ListaPartida
from partidas.jugadores.schema import Jugador
from partidas.utils import armar_broadcast, armador_evento_log, armador_ronda, armador_evento_turno, lista_partidas
from typing import List


partida_no_iniciada = Partida(id=0, nombre="patito", contraseña="123", num_jugadores=5,
                              max_jugadores=6, min_jugadores=4, posiciones=[],
                              turno=0, mazo=None, jugadores=[], iniciada=False, sentido=True)

partida_clockwise = Partida(id=1, nombre="patito", contraseña="123", num_jugadores=5,
                            max_jugadores=6, min_jugadores=4, posiciones=[],
                            turno=0, mazo=None, jugadores=[], iniciada=True, sentido=True)

partida_counter_clockwise = Partida(id=2, nombre="patito", contraseña="123", num_jugadores=5,
                                    max_jugadores=6, min_jugadores=4, posiciones=[],
                                    turno=3, mazo=None, jugadores=[], iniciada=True, sentido=False)

partida_clockwise_borde = Partida(id=3, nombre="patito", contraseña="123", num_jugadores=5,
                                  max_jugadores=6, min_jugadores=4, posiciones=[],
                                  turno=4, mazo=None, jugadores=[], iniciada=True, sentido=True)

partida_counter_clockwise_borde = Partida(id=4, nombre="patito", contraseña="123", num_jugadores=5,
                                          max_jugadores=6, min_jugadores=4, posiciones=[],
                                          turno=0, mazo=None, jugadores=[], iniciada=True, sentido=False)

lista_partidas.append(partida_no_iniciada)
lista_partidas.append(partida_clockwise)
lista_partidas.append(partida_counter_clockwise)
lista_partidas.append(partida_clockwise_borde)
lista_partidas.append(partida_counter_clockwise_borde)

app = FastAPI()

@app.get("/")
async def hub():
    return{"message" : "hola che"}

@app.patch("/partidas/{id_partida}/finalizar_turno", status_code=200)
async def fin_turno(id_partida: int):

    # Obtengo la partida deseada mediante el id con {id_partida}
    index = lista_partidas.get_index_by_id(id_param=id_partida)
    if index == -1:
        raise HTTPException(status_code=404, detail=f"ID ({id_partida}) Not Found")
    
    # Esto es una REFERENCIA a la partida, ergo los cambios se reflejan en el objeto original
    _partida_ : Partida = lista_partidas.get_partida_by_index(index)

    # Verifico si aún no ha iniciado la partida, en cuyo caso arrojo 422 (Bad Entity)
    if not _partida_.esta_iniciada():
        raise HTTPException(status_code=422, detail="Game Not Yet Started")
    
    #  Primero necesito saber cuántos jugadores hay, ya que dados N jugadores presentes
    # en la partida, las posiciones estarán definidas de 0 a N - 1 clockwise 
    ultima_posicion : int = _partida_.get_num_jugadores() - 1

    turno_por_terminar : int = _partida_.get_turno()

    # Reseteo los contadores de acciones de todos
    lista_jugadores: List[Jugador] = _partida_.obtener_jugadores()
    for each in lista_jugadores:
        each.resetear_acciones()
        # Checheamos si hay que sacarlo de la cuarentena
        if (each.get_posicion() == turno_por_terminar and
            each.esta_en_cuarentena()):
            each.rondas_en_cuarentena -= 1

            if each.rondas_en_cuarentena <= 0:
                each.sacar_de_cuarentena()
                # Descartamos la carta de cuarentena
                mazo = _partida_.get_mazo()
                mazo.discard_played_card("Cuarentena")
                armar_broadcast(_partida_= _partida_,
                                msg=armador_evento_log(jugador=each,
                                                       message=f"{each.get_nombre()} salió de cuarentena"),
                                event_name="Log")
                armar_broadcast(_partida_= _partida_,
                                msg=armador_ronda(_partida_.get_id()),
                                event_name="Ronda")
                                
    proximo_turno : int

    #  Si el sentido es positivo/clockwise (True), sumo 1 al turno salvo que se trate de la ultima
    # posición, en cuyo caso el turno pasa a tenerlo quien se encuentre en la primera posición (0)
    if _partida_.get_sentido() == True:
        if turno_por_terminar == ultima_posicion:
            proximo_turno = 0
        else:
            proximo_turno = turno_por_terminar + 1
    #  Si el sentido es negativo/counter-clockwise (False), sustraigo 1 al turno salvo que se trate de
    # la primera posición, en cuyo caso el turno pasa a tenerlo quien se encuentre en la última posición
    else:
        if turno_por_terminar == 0:
            proximo_turno = ultima_posicion
        else:
            proximo_turno = turno_por_terminar - 1
    
    # Los cambios a 
    _partida_.set_turno(proximo_turno)

    # Enviamos evento log de turno
    jugador_turno = _partida_.buscar_jugador_por_posicion(proximo_turno)
    armar_broadcast(_partida_=_partida_,
                    msg=armador_evento_log(jugador=jugador_turno, context="comienzo_turno"), 
                    event_name="Log")

    return