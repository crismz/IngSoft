import sys
from main_test import app
sys.path.append("../..")
from fastapi.testclient import TestClient
from partidas.mazo.cartas.schema import CardSchema
from partidas.mazo.schema import Mazo


client : TestClient = TestClient(app)

# Crear la partida con la base de datos vacia asi el 
# Indice siempre es 1

# Toda combinacion de min_jugadores y max_jugadores
# Medio redundante porque importa el j nomas
# Pero bueno

players : [(int, int)] = [
        (i, j)
        for i in range(4, 13)
        for j in range(4, 13)
    ]

def test_get_deck_is_created():
    for i,j in players:
        mazardo : Mazo = Mazo()
        mazardo.create_deck(1,j)
        assert Mazo is not None and mazardo.cards is not None

def test_existen_cartas():
    for i,j in players:
        mazardo : Mazo = Mazo()
        assert Mazo is not None
        mazardo.create_deck(1,j)
        for card in mazardo.cards:
            assert card is not None
            assert card.get_numplayers() <= j

def test_correct_first_cards():
    for i,j in players:
        mazo : Mazo = Mazo()
        assert mazo is not None
        mazo.create_deck(1,j)
        for k in range(0, j*4):
            card : CardSchema = mazo.take_card()
            assert (
                card.get_type() != "Panico" and
                card.get_name() != "Infectado"
            ) or card.get_id() == 1

def test_take_card():
    for i,j in players:
        mazardo : Mazo = Mazo()
        mazardo.create_deck(1,j)
        assert mazardo.take_card() is not None

def test_take_card_from_empty_deck():   
    for i,j in players:
        mazo: Mazo = Mazo()
        mazo.create_deck(1,j)
        for _ in mazo.cards:
            mazo.take_card()
        assert mazo.len() != 0

def test_discard():
    for i,j in players:
        mazo: Mazo = Mazo()
        mazo.create_deck(1,j)
        card : CardSchema = mazo.take_card()
        mazo.discard_card(card)
        print(card)
        assert (len(mazo.discarded_cards) > 0 and
                mazo.discarded_cards[0] == card)

def test_the_thing_card_in_the_right_positions():
    ''' 
    checkea si la carta de la cosa esta en las primeras
    4 * numero_de_jugadores posiciones, asi siempre
    termina en la mano de un jugador
    
    '''
    for i,j in players:
        mazo: Mazo = Mazo()
        mazo.create_deck(1,j)
        is_there: bool = False
        for k in range(0, j * 4):
            is_there = mazo.cards[k].id == 1
            if is_there:
                break
        assert is_there

def test_ver_mazo_partida_iniciada():
    response_ver_mazo = client.get(f"partidas/{1}/mazo/ver")
    assert response_ver_mazo.status_code == 200

def test_ver_mazo_partida_no_iniciada():
    response_ver_mazo = client.get(f"partidas/{2}/mazo/ver")
    assert response_ver_mazo.status_code == 422

def test_ver_mazo_partida_iniciada_sin_mazo():
    response_ver_mazo = client.get(f"partidas/{3}/mazo/ver")
    assert response_ver_mazo.status_code == 404