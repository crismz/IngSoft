from fastapi import FastAPI, HTTPException, testclient
import requests
import random
from sys import path
path.append("../..")
from partidas.utils import lista_partidas
from partidas.schema import Partida
from partidas.croupier.utils import diccionario_croupier
from partidas.croupier.schema import Croupier
from main import app
#from test_main import app

#client = testclient.TestClient(app)

def test_discard_card_game_not_started():
    response = requests.patch("http://127.0.0.1:8000/partidas/0/jugadores/0/descartar?id_carta=1")
    print(response.json().get("detail"))
    assert response.status_code == 422      

def test_discard_card_player_not_in_game():
    response = requests.patch(f"http://127.0.0.1:8000/partidas/1/jugadores/{random.randint(5,12)}/descartar?id_carta=1")
    assert response.status_code == 404      

def test_discard_card_game_correct_id():
    for player_id in range(0,5): 
        for card_id in range(1,5):
            response = requests.patch(f"http://127.0.0.1:8000/partidas/1/jugadores/{player_id}/descartar?id_carta={card_id}")
            print(response.json().get("detail"))
            assert response.status_code == 200

def test_discard_card_from_empty_hand():
    for player_id in range(0,5): 
        for card_id in range(1,5):
            response = requests.patch(f"http://127.0.0.1:8000/partidas/1/jugadores/{player_id}/descartar?id_carta={card_id}")
            print(response.json().get("detail"))
            assert response.json().get("detail") == f"Card ID ({card_id}) Not Found in Player({player_id})'s Hand"
            assert response.status_code == 404
'''
def test_descartar_carta_partida_no_iniciada():

    json = {
        "nombre_partida": "lacampora_gaming",
        "contraseña": "123",
        "max_jugadores": 12,
        "min_jugadores": 4,
        "nombre_jugador": "epic_gamer" 
    }

    response_create = client.post("http://127.0.0.1:8000/partidas/crear", json=json)
    assert response_create.status_code == 201
    
    id_partida : int = response_create.json().get("id_partida")
    id_jugador : int = response_create.json().get("id_jugador")
    
    print(response_create.json())

    response = client.patch(f"/partidas/{id_partida}/jugadores/{id_jugador}/descartar", json={"id_carta": 1})
    
    print(response.json())
    
    assert response.status_code == 422


def test_descartar_carta_partida_iniciada():
        # Creamos una partida
        json = {
            "nombre_partida": "lacampora_gaming",
            "contraseña": "123",
            "max_jugadores": 12,
            "min_jugadores": 4,
            "nombre_jugador": "epic_gamer"
        }
    
        response_create = client.post("http://127.0.0.1:8000/partidas/crear", json=json)
        assert response_create.status_code == 201

        id_partida : int = response_create.json().get("id_partida")

        # Incluimos 11 jugadores mas
        for i in range(1,12):
            name = f"jugador_{i}"
            json_join = {
                "nombre_jugador": name,
                "contraseña": "123"
            }

            response_join = client.post(f"http://127.0.0.1:8000/partidas/{id_partida}/unir", json=json_join)
            print(response_join.json())
            assert response_join.status_code == 201

        response_start = client.patch(f"http://127.0.0.1:8000/partidas/{id_partida}/iniciar", 
                                      json={"id_partida": id_partida, "id_jugador": 0})
        assert response_start.status_code == 200

        partida : Partida = lista_partidas.get_partida_by_index(lista_partidas.get_index_by_id(id_partida))
        #croupier : Croupier = diccionario_croupier.get_croupier(lista_partidas.get_index_by_id(id_partida))
    
        # Chequeamos que la partida esté iniciada
        assert partida.esta_iniciada()

        for i in range(13):
                num : int = random.randint(1, 108)
                response_descartar = client.patch(f"http://127.0.0.1:8000/partidas/{id_partida}/jugadores/{i}/descartar", 
                                        json={"id_card": num, "id_partida": id_partida, "id_jugador": 0})
                
                print(response_descartar.json())
                
                assert (response_descartar.status_code == 422)
'''