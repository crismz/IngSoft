import sys
sys.path.append("../..")

from partidas.schema import Partida, ListaPartida, Posicion
from partidas.jugadores.schema import Jugador
from partidas.croupier.schema import DiccionarioCroupier
from partidas.mazo.schema import Mazo
from partidas.mazo.cartas.schema import CardSchema

from partidas.schema import Partida
from abc import ABC, abstractmethod

# Jugadores
lista_jugadores = [Jugador(id=0, nombre="Ironclad", posicion=0, rol="La Cosa", mano=[], cuarentena=True), 
                   Jugador(id=1, nombre="Silent", posicion=1, rol="Humano", mano=[]),
                   Jugador(id=2, nombre="Defect", posicion=2, rol="Infectado", mano=[]),
                   Jugador(id=3, nombre="Watcher", posicion=3, rol="Humano", mano=[]),
                   Jugador(id=4, nombre="Kelsier", posicion=4, rol="Humano", mano=[]),
                   Jugador(id=5, nombre="Vin", posicion=5, rol="Humano", mano=[]),
                   Jugador(id=6, nombre="Spook", posicion=6, rol="Humano", mano=[])]

lista_jugadores2 = [Jugador(id=0, nombre="Ironclad", posicion=0, rol="La Cosa", mano=[], cuarentena=True), 
                   Jugador(id=1, nombre="Silent", posicion=1, rol="Humano", mano=[]),
                   Jugador(id=2, nombre="Defect", posicion=2, rol="Infectado", mano=[]),
                   Jugador(id=3, nombre="Watcher", posicion=3, rol="Humano", mano=[]),
                   Jugador(id=4, nombre="Kelsier", posicion=4, rol="Humano", mano=[]),
                   Jugador(id=5, nombre="Vin", posicion=5, rol="Humano", mano=[]),
                   Jugador(id=6, nombre="Spook", posicion=6, rol="Humano", mano=[]),
                   Jugador(id=7, nombre="Sazed", posicion=7, rol="Humano", mano=[])]


lista_partidas = ListaPartida()

partida1 = Partida(id=0, nombre="patito", contraseña="123", num_jugadores=0,
                          max_jugadores=7, min_jugadores=4, posiciones=[],
                          turno=0, mazo=Mazo(), jugadores=[], iniciada=True, conexiones={})

partida2 = Partida(id=1, nombre="patito2", contraseña="123", num_jugadores=0,
                    max_jugadores=8, min_jugadores=4, posiciones=[],
                    turno=5, mazo=Mazo(), jugadores=[], iniciada=True, conexiones={})


puerta = CardSchema(id=86,
                    num_players=partida1.get_num_jugadores(),
                    type="Obstaculo",
                    name="Puerta atrancada",
                    effect="Se descarta sin afectar la partida",
                    target="neighbour")

cuarentena = CardSchema(id=85,
                        num_players=partida1.get_num_jugadores(),
                        type="Obstaculo",
                        name="Cuarentena",
                        effect="Se descarta sin afectar la partida",
                        target="neighbour")

mazo1 = partida1.get_mazo()
mazo2 = partida2.get_mazo()

mazo1.play_card(puerta.model_copy())
mazo1.play_card(puerta.model_copy())
mazo1.play_card(cuarentena.model_copy())

mazo2.play_card(puerta.model_copy())
mazo2.play_card(puerta.model_copy())
mazo2.play_card(cuarentena.model_copy())

posicion_vacia = Posicion()
posicion_bloqueada_der = Posicion()
posicion_bloqueada_der.bloquear_pos(1)
posicion_bloqueada_izq = Posicion()
posicion_bloqueada_izq.bloquear_pos(0)

for each in range(len(lista_jugadores)):
    jugador = lista_jugadores[each]
    partida1.agregar_jugador(jugador)

for each in range(len(lista_jugadores2)):
    jugador = lista_jugadores2[each]
    partida2.agregar_jugador(jugador)

partida1.agregar_posicion(posicion_bloqueada_der)
partida1.agregar_posicion(posicion_bloqueada_izq)
for i in range(5):
    partida1.agregar_posicion(posicion_vacia.model_copy())

partida2.agregar_posicion(posicion_bloqueada_der)
partida2.agregar_posicion(posicion_bloqueada_izq)
for i in range(6):
    partida2.agregar_posicion(posicion_vacia.model_copy())

# Repartir las cartas que queremos que estén en las manos de los jugadores
for each in partida1.obtener_jugadores():
    vigila = CardSchema(id=48,
                        num_players=partida1.get_num_jugadores(),
                        type="Accion",
                        name="Vigila tus Espaldas",
                        effect="Da vuelta el sentido de la ronda",
                        target="any"
                        )
    fiesta = CardSchema(id=95,
                        num_players=partida1.get_num_jugadores(),
                        type="Panico",
                        name="Aquí Fiesta",
                        effect="Descarta todas las cartas de puerta atrancada y cuarentena y cambios de lugar", 
                        target="self")
    cambio = CardSchema(id=50,
                    num_players=partida1.get_num_jugadores(),
                    type="Accion",
                    name="Cambio de Lugar",
                    effect="Cambia con alguien adyacente",
                    target="neighbour"
                    )
    
    corras = CardSchema(id=55,
                    num_players=partida1.get_num_jugadores(),
                    type="Accion",
                    name="Más Vale Corras",
                    effect="Cambia con alguien que no esté en cuarentena",
                    target="any"
                    )

    each.agregar_carta_mano(vigila)
    each.agregar_carta_mano(fiesta)
    each.agregar_carta_mano(cambio)
    each.agregar_carta_mano(corras)

for each in partida2.obtener_jugadores():
    vigila = CardSchema(id=48,
                        num_players=partida1.get_num_jugadores(),
                        type="Accion",
                        name="Vigila tus Espaldas",
                        effect="Da vuelta el sentido de la ronda",
                        target="any"
                        )
    fiesta = CardSchema(id=95,
                        num_players=partida1.get_num_jugadores(),
                        type="Panico",
                        name="Aquí Fiesta",
                        effect="Descarta todas las cartas de puerta atrancada y cuarentena y cambios de lugar", 
                        target="self")
    cambio = CardSchema(id=50,
                    num_players=partida1.get_num_jugadores(),
                    type="Accion",
                    name="Cambio de Lugar",
                    effect="Cambia con alguien adyacente",
                    target="neighbour"
                    )
    
    corras = CardSchema(id=55,
                    num_players=partida1.get_num_jugadores(),
                    type="Accion",
                    name="Más Vale Corras",
                    effect="Cambia con alguien que no esté en cuarentena",
                    target="any"
                    )

    each.agregar_carta_mano(vigila)
    each.agregar_carta_mano(fiesta)
    each.agregar_carta_mano(cambio)
    each.agregar_carta_mano(corras)
    
lista_partidas.append(partida1)
lista_partidas.append(partida2)
# Crear el diccionario de croupiers
diccionario_croupier = DiccionarioCroupier()
# Añadir el diccionario de croupiers de la partida
diccionario_croupier.append(partida1)
diccionario_croupier.append(partida2)

class CardEffect(ABC):
    @abstractmethod
    def verificar(self, id_carta:int, id_jugador: int, id_objetivo: int, partida: Partida):
        pass

    @abstractmethod
    def aplicar(self, id_objetivo: int, partida: Partida):
        pass

class AquiFiesta(CardEffect):
    def verificar(self, id_carta: int, id_jugador: int, id_objetivo: int, partida: Partida):
        if id_carta not in range(95, 97):
            return False

        return True
    
    def aplicar(self, id_objetivo: int, partida: Partida):
        # Descarto todas las cartas de puerta atrancada y cuarentena
        mazo = partida.get_mazo()
        mazo.discard_played_cards()

        # Desbloqueamos todas las posiciones
        partida.desbloquear_posiciones()
        # Sacamos de cuarentena a todos los jugadores
        for each in partida.get_jugadores():
            each.sacar_de_cuarentena()

        # Obtenemos id de jugador en turno
        jugador_turno = partida.buscar_jugador_por_posicion(partida.get_turno())
        # Obtenemos la cantidad de jugadores
        num_jugadores = partida.get_num_jugadores()
        # Contador para intercambios
        i = 0
        # Posicion de donde comienza los intercambios
        pos_actual = partida.get_turno()

        while i < partida.get_num_jugadores() // 2:
            # Buscamos el jugador de pos_actual y su siguiente
            jugador1 = partida.buscar_jugador_por_posicion(pos_actual)
            jugador2 = partida.buscar_jugador_por_posicion((pos_actual+1)%num_jugadores)
            # Intercambiamos sus posiciones
            pos_aux = jugador1.get_posicion()
            jugador1.set_posicion(jugador2.get_posicion())
            jugador2.set_posicion(pos_aux)

            # Sumamos a i, y la posicion
            i += 1
            pos_actual = (pos_actual + 2) % num_jugadores
        
        # Seteamos el turno al jugador que tiene el turno
        partida.set_turno(jugador_turno.get_posicion())


def test_jugadores_impar():
    fiesta = AquiFiesta()
    fiesta.aplicar(0, partida1)

    # Chequeamos que todas las played_cards hayan sido descartadas
    assert(partida1.get_mazo().played_cards == [])
    # Chequeamos que no haya ningun bloqueo
    assert(partida1.hay_bloqueo(0, 1) == False)
    assert(partida1.hay_bloqueo(1, 2) == False)
    assert(partida1.hay_bloqueo(2, 3) == False)
    assert(partida1.hay_bloqueo(3, 4) == False)
    assert(partida1.hay_bloqueo(4, 5) == False)
    assert(partida1.hay_bloqueo(5, 6) == False)
    assert(partida1.hay_bloqueo(6, 0) == False)
    # Chequeamos que todos los jugadores esten fuera de cuarentena
    assert(partida1.buscar_jugador(0).esta_en_cuarentena() == False)
    # Chequeamos que los jugadores hayan intercambiado sus posiciones
    assert(partida1.buscar_jugador(0).get_posicion() == 1)
    assert(partida1.buscar_jugador(1).get_posicion() == 0)
    assert(partida1.buscar_jugador(2).get_posicion() == 3)
    assert(partida1.buscar_jugador(3).get_posicion() == 2)
    assert(partida1.buscar_jugador(4).get_posicion() == 5)
    assert(partida1.buscar_jugador(5).get_posicion() == 4)
    assert(partida1.buscar_jugador(6).get_posicion() == 6)
    # Chequeamos que el turno sea del jugador 0
    id_turno = partida1.buscar_jugador_por_posicion(partida1.get_turno()).get_id()
    assert(partida1.get_turno() == partida1.buscar_jugador(id_turno).get_posicion())

def test_jugadores_par():
    fiesta = AquiFiesta()
    fiesta.aplicar(0, partida2)

    # Chequeamos que todas las played_cards hayan sido descartadas
    assert(partida2.get_mazo().played_cards == [])
    # Chequeamos que no haya ningun bloqueo
    assert(partida2.hay_bloqueo(0, 1) == False)
    assert(partida2.hay_bloqueo(1, 2) == False)
    assert(partida2.hay_bloqueo(2, 3) == False)
    assert(partida2.hay_bloqueo(3, 4) == False)
    assert(partida2.hay_bloqueo(4, 5) == False)
    assert(partida2.hay_bloqueo(5, 6) == False)
    assert(partida2.hay_bloqueo(6, 7) == False)
    assert(partida2.hay_bloqueo(7, 0) == False)
    # Chequeamos que todos los jugadores esten fuera de cuarentena
    assert(partida2.buscar_jugador(0).esta_en_cuarentena() == False)
    # Chequeamos que los jugadores hayan intercambiado sus posiciones
    assert(partida2.buscar_jugador(5).get_posicion() == 6)
    assert(partida2.buscar_jugador(6).get_posicion() == 5)
    assert(partida2.buscar_jugador(7).get_posicion() == 0)
    assert(partida2.buscar_jugador(0).get_posicion() == 7)
    assert(partida2.buscar_jugador(1).get_posicion() == 2)
    assert(partida2.buscar_jugador(2).get_posicion() == 1)
    assert(partida2.buscar_jugador(3).get_posicion() == 4)
    assert(partida2.buscar_jugador(4).get_posicion() == 3)
    # Chequeamos que el turno sea del jugador 5
    id_turno = partida2.buscar_jugador_por_posicion(partida2.get_turno()).get_id()
    assert(partida2.get_turno() == partida2.buscar_jugador(id_turno).get_posicion())