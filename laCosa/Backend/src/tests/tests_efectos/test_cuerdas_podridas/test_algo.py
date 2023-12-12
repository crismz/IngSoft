from main_test import partida_ejemplo
import sys
sys.path.append("../../..")
from partidas.mazo.schema import Mazo
from partidas.mazo.cartas.schema import CardSchema 

def sacar_cuarentena():
    for jugador in partida_ejemplo.get_jugadores():
            if jugador.esta_en_cuarentena():
                jugador.sacar_de_cuarentena()
    partida_ejemplo.mazo.discard_played_card("Cuarentena")

def test_algoritmo():
    sacar_cuarentena()
    for jugador in partida_ejemplo.get_jugadores():
        assert not jugador.esta_en_cuarentena()
    for card in partida_ejemplo.get_mazo().played_cards:
        assert card.get_name() != "Cuarentena"
