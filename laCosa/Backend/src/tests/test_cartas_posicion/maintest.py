import sys
sys.path.append("../..")

from partidas.schema import Partida, ListaPartida, Posicion
from partidas.jugadores.schema import Jugador
from partidas.croupier.schema import DiccionarioCroupier
from partidas.mazo.schema import Mazo
from partidas.mazo.cartas.schema import CardSchema


lista_jugadores = []

lista_jugadores.append(Jugador(id=0, nombre="C. Auguste Dupin", posicion=0, rol="Human"))
lista_jugadores.append(Jugador(id=1, nombre="Sherlock Holmes", posicion=1, rol="Human"))
lista_jugadores.append(Jugador(id=2, nombre="Long John Silver", posicion=2, rol="Human", cuarentena=True))
lista_jugadores.append(Jugador(id=3, nombre="Kelsier", posicion=3, rol="Human"))


lista_partidas = ListaPartida()

partida = Partida(id=0, nombre="patito", contraseña="123", num_jugadores=4,
                          max_jugadores=6, min_jugadores=4, posiciones=[],
                          turno=0, mazo=None, jugadores=[], iniciada=True, conexiones={})

posicion_bloqueada_der = Posicion()
posicion_bloqueada_der.bloquear_pos(1)
posicion_bloqueada_izq = Posicion()
posicion_bloqueada_izq.bloquear_pos(0)

for each in range(len(lista_jugadores)):
    jugador = lista_jugadores[each]
    partida.agregar_jugador(jugador)

partida.agregar_posicion(posicion_bloqueada_izq)
partida.agregar_posicion(Posicion())
partida.agregar_posicion(Posicion())
partida.agregar_posicion(posicion_bloqueada_der)


current_mazo = Mazo(id_partida=0)
partida.set_mazo(current_mazo)
# Repartir las cartas que queremos que estén en las manos de los jugadores
for each in partida.obtener_jugadores():
    vigila = CardSchema(id=48,
                        num_players=partida.get_num_jugadores(),
                        type="Accion",
                        name="Vigila tus Espaldas",
                        effect="Da vuelta el sentido de la ronda",
                        target="any"
                        )
    uno_dos = CardSchema(id=91,
                        num_players=partida.get_num_jugadores(),
                        type="Panico",
                        name="Uno, dos...",
                        effect="Cambia con el tercero a tu izquierda o derecha",
                        target="direction")
    cambio = CardSchema(id=50,
                    num_players=partida.get_num_jugadores(),
                    type="Accion",
                    name="Cambio de Lugar",
                    effect="Cambia con alguien adyacente",
                    target="neighbour"
                    )
    
    corras = CardSchema(id=55,
                    num_players=partida.get_num_jugadores(),
                    type="Accion",
                    name="Más Vale Corras",
                    effect="Cambia con alguien que no esté en cuarentena",
                    target="any"
                    )

    each.agregar_carta_mano(vigila)
    each.agregar_carta_mano(uno_dos)
    each.agregar_carta_mano(cambio)
    each.agregar_carta_mano(corras)

    
lista_partidas.append(partida)
# Crear el diccionario de croupiers
diccionario_croupier = DiccionarioCroupier()
# Añadir el diccionario de croupiers de la partida
diccionario_croupier.append(partida)

from partidas.schema import Partida
from abc import ABC, abstractmethod

class CardEffect(ABC):
    @abstractmethod
    def verificar(self, id_carta:int, id_jugador: int, id_objetivo: int, partida: Partida):
        pass

    @abstractmethod
    def aplicar(self, id_objetivo: int, partida: Partida):
        pass
    
class Vigila(CardEffect):
    def verificar(self, id_carta: int, id_jugador: int, id_objetivo: int, partida: Partida):

        if id_carta not in range(48, 50):
            return False
        
        return True

    def aplicar(self, id_objetivo: int, partida: Partida):
        # Cambiamos el orden de la ronda
        partida.set_sentido(not partida.get_sentido())
        return

class Posicion(CardEffect):
    def aplicar(self, id_objetivo: int, partida: Partida):
        # Obtenemos a ambos jugadores
        jugador_turno = partida.buscar_jugador_por_posicion(partida.get_turno())
        jugador_objetivo = partida.buscar_jugador(id_objetivo)
        if (not jugador_turno.esta_en_cuarentena() 
            and not jugador_objetivo.esta_en_cuarentena()):
            # Intercambiamos sus posiciones
            pos_aux = jugador_turno.get_posicion()
            jugador_turno.set_posicion(jugador_objetivo.get_posicion())
            jugador_objetivo.set_posicion(pos_aux)
            # Seteamos el turno al jugador que tiene el turno
            partida.set_turno(jugador_turno.get_posicion())
        return
    
class CambioLugar(Posicion):
    def verificar(self, id_carta: int, id_jugador: int, id_objetivo: int, partida: Partida):

        if id_carta not in range(50, 55):
            return False
        
        if id_jugador == id_objetivo:
            return False
        
        jugador = partida.buscar_jugador(id_jugador)
        objetivo = partida.buscar_jugador(id_objetivo)

        # Obtenemos las posiciones de los jugadores
        posicion_jugador = jugador.get_posicion()
        posicion_objetivo = objetivo.get_posicion()

        # Chequeamos si los jugadores son adyacentes
        if not partida.son_adyacentes(posicion_jugador, posicion_objetivo):
            return False

        # Chequear si el jugador objetivo está en cuarentena
        if partida.buscar_jugador(id_jugador=id_objetivo).esta_en_cuarentena():
            return False
        
        # Chequear por puerta atrancada
        if partida.hay_bloqueo(id_jugador, id_objetivo):
            return False

        return True
    
class MasValeCorras(Posicion):
    def verificar(self, id_carta: int, id_jugador: int, id_objetivo: int, partida: Partida):

        if id_carta not in range(55, 60):
            return False
        
        if id_jugador == id_objetivo:
            return False

        # Verificar si el jugador objetivo está en cuarentena
        if partida.buscar_jugador(id_jugador=id_objetivo).esta_en_cuarentena():
            return False

        return True

class UnoDos(Posicion):
    def verificar(self, id_carta: int, id_jugador: int, id_objetivo: int, partida: Partida):

        if id_carta not in range(91, 93):
            return False
        
        if id_jugador == id_objetivo:
            return False

        # Verificamos que el jugador objetivo es el tercero,
        # ya sea a la izquierda o a la derecha
        num_jugadores = partida.get_num_jugadores()
        pos_objetivo = partida.buscar_jugador(id_objetivo).get_posicion()
        pos_jugador = partida.buscar_jugador(id_jugador).get_posicion()

        if ((pos_jugador + 3) % num_jugadores != pos_objetivo and 
            (pos_jugador - 3) % num_jugadores != pos_objetivo):
            return False

        return True
    
## Tests
def test_vigila():
    vigilacion = Vigila()

    sentido = partida.get_sentido()

    assert vigilacion.verificar(id_carta=48, id_jugador=0, id_objetivo=1, partida=partida) == True
    assert vigilacion.verificar(id_carta=20, id_jugador=0, id_objetivo=1, partida=partida) == False
    vigilacion.aplicar(id_objetivo=1, partida=partida)

    assert sentido == (not partida.get_sentido())

def test_cambio():
    cambio = CambioLugar()

    # Chequear que la carta sea válida
    assert cambio.verificar(id_carta=50, id_jugador=0, id_objetivo=1, partida=partida) == True
    assert cambio.verificar(id_carta=20, id_jugador=0, id_objetivo=1, partida=partida) == False
    
    # Chequear que el jugador no se cambie a sí mismo
    assert cambio.verificar(id_carta=50, id_jugador=0, id_objetivo=0, partida=partida) == False
    
    # Chequear que el jugador no se cambie con alguien que no sea adyacente
    assert cambio.verificar(id_carta=50, id_jugador=0, id_objetivo=2, partida=partida) == False
    
    # Chequear que el jugador no se cambie con alguien que tiene puerta atrancada
    assert cambio.verificar(id_carta=50, id_jugador=0, id_objetivo=3, partida=partida) == False
    
    # Chequear que el jugador no se cambie con alguien que esté en cuarentena
    assert cambio.verificar(id_carta=50, id_jugador=1, id_objetivo=2, partida=partida) == False

    cambio.aplicar(id_objetivo=1, partida=partida)

    assert partida.buscar_jugador(0).get_posicion() == 1
    assert partida.buscar_jugador(1).get_posicion() == 0

def test_mas_vale_corras():
    corras = MasValeCorras()

    # Chequear que la carta sea válida
    assert corras.verificar(id_carta=56, id_jugador=0, id_objetivo=1, partida=partida) == True
    assert corras.verificar(id_carta=20, id_jugador=0, id_objetivo=1, partida=partida) == False

    # Chequear que el jugador no se cambie a sí mismo
    assert corras.verificar(id_carta=50, id_jugador=0, id_objetivo=0, partida=partida) == False

    # Chequear que el jugador no se cambie con alguien que esté en cuarentena
    assert corras.verificar(id_carta=50, id_jugador=1, id_objetivo=2, partida=partida) == False

    partida.buscar_jugador(2).sacar_de_cuarentena()

    pos_jugador_0 = partida.buscar_jugador(0).get_posicion()
    pos_jugador_2 = partida.buscar_jugador(2).get_posicion()

    corras.aplicar(id_objetivo=2, partida=partida)

    assert partida.buscar_jugador(0).get_posicion() == pos_jugador_2
    assert partida.buscar_jugador(2).get_posicion() == pos_jugador_0
    
def test_uno_dos():
    uno_dos = UnoDos()

    # Seteamos de nuevo las posiciones a las originales
    for i in range(4):
        partida.buscar_jugador(i).set_posicion(i)

    partida.set_turno(0)

    # Chequear que la carta sea válida
    assert uno_dos.verificar(id_carta=91, id_jugador=0, id_objetivo=3, partida=partida) == True
    assert uno_dos.verificar(id_carta=20, id_jugador=0, id_objetivo=1, partida=partida) == False

    # Chequear que el jugador no se cambie a sí mismo
    assert uno_dos.verificar(id_carta=91, id_jugador=0, id_objetivo=0, partida=partida) == False

    # Chequear que el jugador no se cambie con alguien que no sea el tercero
    assert uno_dos.verificar(id_carta=91, id_jugador=0, id_objetivo=1, partida=partida) == False
    assert uno_dos.verificar(id_carta=91, id_jugador=0, id_objetivo=2, partida=partida) == False
    assert uno_dos.verificar(id_carta=91, id_jugador=0, id_objetivo=3, partida=partida) == True

    partida.buscar_jugador(3).poner_en_cuarentena()

    pos_jugador_0 = partida.buscar_jugador(0).get_posicion()
    pos_jugador_3 = partida.buscar_jugador(3).get_posicion()
    
    # Chequeamos que con cuarentena no haga efecto
    uno_dos.aplicar(id_objetivo=3, partida=partida)
    assert partida.buscar_jugador(0).get_posicion() == pos_jugador_0
    assert partida.buscar_jugador(3).get_posicion() == pos_jugador_3

    partida.buscar_jugador(3).sacar_de_cuarentena()

    # Chequeamos el efecto normal
    uno_dos.aplicar(id_objetivo=3, partida=partida)
    
    assert partida.buscar_jugador(0).get_posicion() == pos_jugador_3
    assert partida.buscar_jugador(3).get_posicion() == pos_jugador_0