from typing import List, Optional, Tuple
from pydantic import BaseModel, Field

import sys
sys.path.append("../../../")

from partidas.mazo.schema import Mazo

class Posicion(BaseModel):
    pos: Tuple[bool, bool] = [True, True]

    def get(self, lado: int):
        return self.pos[lado]

    def bloquear_pos(self, lado: int):
        self.pos[lado] =  True
    
    def desbloquear_pos(self, lado: int):
        self.pos[lado] =  False

class Jugador(BaseModel):
    id: int
    nombre: str
    posicion: int = None
    rol: str = None
    #mano: Optional[List[CardSchema]] = Field(default_factory=list)
    cuarentena: bool = False
    # Datos para poder intercambiar cartas
    id_carta_intercambio: int = None
    id_objetivo_intercambio: int = -1 
    # -1 quiere decir "objetivo por defecto" aka el que sigue en la ronda
    rondas_en_cuarentena: int = 0

    def poner_en_cuarentena(self):
        self.cuarentena = True
        self.rondas_en_cuarentena = 2

    def sacar_de_cuarentena(self):
        self.cuarentena = False
        self.rondas_en_cuarentena = 0

    def get_posicion(self) -> int:
        return self.posicion
    def get_mazo(self) -> int:
        return self.mazo
    get_id = lambda self: self.id

class partida_lite(BaseModel):
    id: Optional[int] = None
    posiciones: Optional[List[Posicion]] = Field(default_factory=list)
    turno: Optional[int] = 0
    sentido: Optional[bool] = False
    #mazo: Optional[Mazo] = None
    jugadores: Optional[List[Jugador]] = Field(default_factory=list)
    num_jugadores: Optional[int] = 0
    num_jugadores_inicial: Optional[int] = 0
    mazo: Mazo = Mazo()
    def get_id(self) -> int:
        return self.id
    def get_mazo(self) -> Mazo:
        return self.mazo
    def son_adyacentes(self, posicion_a: int, posicion_b: int) -> bool:
        # NOTA: Estos comentarios se deberían borrar en la PR
        # Chequeamos que el input es válido
        cantidad_jugadores = self.get_num_jugadores()
        if posicion_a < 0 or posicion_a >= cantidad_jugadores:
            return False
        if posicion_b < 0 or posicion_b >= cantidad_jugadores:
            return False

        diferencia = abs(posicion_a-posicion_b)
        adyacentes = diferencia == 1 or diferencia == cantidad_jugadores-1
        return adyacentes
    
    def buscar_jugador(self, id_jugador: int) -> Optional[Jugador]:
        result = None
        for each in self.jugadores:
            if each.get_id() == id_jugador:
                result = each 
        return result
    
    def buscar_jugador_por_posicion(self, posicion: int) -> Jugador:
        result = None
        for each in self.jugadores:
            if each.get_posicion() == posicion:
                result = each 
        return result

    def get_num_jugadores_inicial(self) -> int:
        return self.num_jugadores_inicial

    def get_num_jugadores(self) -> int:
        return self.num_jugadores

    def print_positions(self):
        for pos in self.posiciones:
            print(f"{pos.get(0)}, {pos.get(1)}")

    def bloquear_posicion(self, num_pos: int, lado: int):
        # Bloqueamos el lado de la posición dada
        posicion = self.posiciones[num_pos]
        posicion.bloquear_pos(lado)

        cantidad_jugadores = self.get_num_jugadores()
        extremes = [0, cantidad_jugadores-1]          

        # Conseguimos lado contrario
        lado_contrario = abs(lado-1)

        # Conseguimos la posición adyacente 
        # en base a que lado hay que bloquear 
        if lado_contrario == 0:
            # Se bloquea el 0 del siguiente
            if num_pos in extremes:
                self.posiciones[0].bloquear_pos(lado_contrario)
            else:
                self.posiciones[num_pos+1].bloquear_pos(lado_contrario)
        else:
            # Se bloquea el 1 del anterior
            if num_pos in extremes:
                self.posiciones[cantidad_jugadores-1].bloquear_pos(lado_contrario)
            else:
                self.posiciones[num_pos-1].bloquear_pos(lado_contrario)

        return

    def desbloquear_posicion(self, num_pos: int, lado: int):
        # Desbloqueamos el lado de la posición dada
        posicion = self.posiciones[num_pos]
        posicion.desbloquear_pos(lado)     

        # Conseguimos lado contrario
        lado_contrario = abs(lado-1)

        cantidad_jugadores = self.get_num_jugadores()  

        if lado_contrario == 0:
            lado_a_desbloquear = self.posiciones[(num_pos + 1) % cantidad_jugadores]
        elif lado_contrario == 1:
            lado_a_desbloquear = self.posiciones[(num_pos - 1) % cantidad_jugadores]

        lado_a_desbloquear.desbloquear_pos(lado_contrario)

        return


def verificar(id_carta: int, id_jugador: int, id_objetivo: int, partida: partida_lite):
    
    if id_carta not in range(30, 32):
        return False

    # Chequeamos que el jugador objetivo sea adyacente
    
    jugador: Jugador = partida.buscar_jugador(id_jugador)
    objetivo: Jugador = partida.buscar_jugador(id_objetivo)

    posicion_jugador: int = jugador.get_posicion()
    posicion_objetivo: int = objetivo.get_posicion()
        
    if not partida.son_adyacentes(posicion_jugador, posicion_objetivo):
        return False

    return True

def aplicar(posicion_jugador: int, posicion_objetivo: int, partida: partida_lite):

    mazo = partida.get_mazo()

    difference = abs(posicion_jugador - posicion_objetivo)
    if difference == 0:

        partida.desbloquear_posicion(posicion_objetivo, 1)
    
    if (posicion_jugador > posicion_objetivo
        and difference == 1):

        partida.desbloquear_posicion(posicion_objetivo, 1)

    elif (posicion_jugador < posicion_objetivo
        and difference == 1):
        
        partida.desbloquear_posicion(posicion_objetivo, 0)
    
    # Casos bordes
    elif (posicion_jugador > posicion_objetivo
        and difference == partida.get_num_jugadores() - 1):
    
        partida.desbloquear_posicion(posicion_objetivo, 0)
    
    elif (posicion_jugador < posicion_objetivo
        and difference == partida.get_num_jugadores() - 1):
    
        partida.desbloquear_posicion(posicion_objetivo, 1) 

    # Descartamos la carta que esta en juego
    mazo.discard_played_card("Puerta atrancada")
    partida.buscar_jugador_por_posicion(posicion_objetivo).sacar_de_cuarentena()
    # Descartamos la carta que esta en juego
    mazo.discard_played_card("Cuarentena")
    

partida_1 = partida_lite(
    posiciones=[
        # All locked
        Posicion(),
        Posicion(),
        Posicion(),
        Posicion(),
        Posicion(),
        Posicion(),
        Posicion(),
        Posicion()
    ],
    turno=0,
    sentido=False,
    jugadores=[
        Jugador(id=0, nombre="Jugador 0", posicion=0),
        Jugador(id=1, nombre="Jugador 1", posicion=1),
        Jugador(id=2, nombre="Jugador 2", posicion=2),
        Jugador(id=3, nombre="Jugador 3", posicion=3, cuarentena=True),
        Jugador(id=4, nombre="Jugador 4", posicion=4),
        Jugador(id=5, nombre="Jugador 5", posicion=5),
        Jugador(id=6, nombre="Jugador 6", posicion=6),
        Jugador(id=7, nombre="Jugador 7", posicion=7)
    ],
    num_jugadores=8,
    num_jugadores_inicial=8
)

partida_2 = partida_lite(
    posiciones=[
        # All unlocked
        Posicion(),
        Posicion(),
        Posicion(),
        Posicion(),
        Posicion(),
        Posicion(),
        Posicion(),
        Posicion()
    ],
    turno=0,
    sentido=False,
    jugadores=[
        Jugador(id=0, nombre="Jugador 0", posicion=0),
        Jugador(id=1, nombre="Jugador 1", posicion=1),
        Jugador(id=2, nombre="Jugador 2", posicion=2),
        Jugador(id=3, nombre="Jugador 3", posicion=3),
        Jugador(id=4, nombre="Jugador 4", posicion=4),
        Jugador(id=5, nombre="Jugador 5", posicion=5),
        Jugador(id=6, nombre="Jugador 6", posicion=6),
        Jugador(id=7, nombre="Jugador 7", posicion=7)
    ],
    num_jugadores=8,
    num_jugadores_inicial=8
)

'''
[True, True] [True, True] [True, True] [True, True] [True, True] [True, True] [True, True] [True, True]  

'''

def test_not_right_card():
    assert not verificar(85, 0, 1, partida_1)

def test_not_adyacents():
    assert not verificar(30, 0, 2, partida_1)

def test_aplicar_adyacentes_1():

    assert verificar(30, 2, 3, partida_1)
    aplicar(2, 3, partida_1)

    rest_locked: bool = True
    i: int = 0
    for pos in partida_1.posiciones:
        if i in [0,2,3,7]:
            break
        rest_locked = rest_locked and pos.get(0) and pos.get(1)
        i += 1

    assert (partida_1.posiciones[2].get(0) == True and
            partida_1.posiciones[2].get(1) == False and
            partida_1.posiciones[3].get(0) == False and
            partida_1.posiciones[3].get(1) == True and
            rest_locked)

def test_aplicar_adyacentes_caso_borde_1():
    
    assert verificar(30, 7, 0, partida_1)
    aplicar(7, 0, partida_1)
    
    rest_locked: bool = True
    i: int = 0
    for pos in partida_1.posiciones:
        if i in [0,2,3,7]:
            break
        rest_locked = rest_locked and pos.get(0) and pos.get(1)
        i += 1

    assert (partida_1.posiciones[7].get(0) == True and
            partida_1.posiciones[7].get(1) == False and
            partida_1.posiciones[0].get(0) == False and
            partida_1.posiciones[0].get(1) == True and
            rest_locked)
    
def test_aplicar_adyacentes_2():

    assert verificar(30, 2, 3, partida_2)
    aplicar(3, 2, partida_2)

    rest_locked: bool = True
    i: int = 0
    for pos in partida_2.posiciones:
        if i == 0 or i == 1:
            break
        rest_locked = rest_locked and pos.get(0) and pos.get(1)
        i += 1

    assert (partida_2.posiciones[2].get(0) == True and
            partida_2.posiciones[2].get(1) == False and
            partida_2.posiciones[3].get(0) == False and
            partida_2.posiciones[3].get(1) == True and
            rest_locked)

def test_aplicar_adyacentes_caso_borde_2():

    assert verificar(30, 0, 7, partida_2)
    aplicar(0, 7, partida_2)

    rest_locked: bool = True
    i: int = 0
    for pos in partida_1.posiciones:
        if i in [0,2,3,7]:
            break
        rest_locked = rest_locked and pos.get(0) and pos.get(1)
        i += 1
    assert (partida_2.posiciones[7].get(0) == True and
            partida_2.posiciones[7].get(1) == False and
            partida_2.posiciones[0].get(0) == False and
            partida_2.posiciones[0].get(1) == True and
            rest_locked)
    
def test_sacar_de_cuarentena():
    assert verificar(30, 2, 3, partida_1)
    # seteamos al jugador en cuarentena
    partida_1.jugadores[3].cuarentena = True
    assert partida_1.jugadores[3].cuarentena
    aplicar(2, 3, partida_1)
    assert not partida_1.jugadores[3].cuarentena