from fastapi.testclient import TestClient
from main_test import lista_partidas, app

client = TestClient(app)

def test_union_partida_inexistente():
    response = client.post(url="/partidas/5/unir",
                           json={"nombre_jugador": "Brotato",
                                 "contraseña": "123"})
    
    assert response.status_code == 404
    return

def test_union_contraseña_incorrecta():
    response = client.post(url="/partidas/0/unir",
                           json={"nombre_jugador": "Brotato",
                                 "contraseña": "Esta no es"})
    
    assert response.status_code == 400
    return

def test_union_partida_llena():
    response = client.post(url="/partidas/2/unir",
                           json={"nombre_jugador": "Brotato",
                                 "contraseña": "123"})
    
    assert response.status_code == 400
    return

def test_union_partida_iniciada():
    response = client.post(url="/partidas/1/unir",
                           json={"nombre_jugador": "Brotato",
                                 "contraseña": "123"})
    
    assert response.status_code == 422

def test_union_exitosa():
    partida = lista_partidas.get_partida_by_index(0)
    num_jugadores_viejo = partida.get_num_jugadores()

    response = client.post(url="/partidas/0/unir",
                           json={"nombre_jugador": "Brotato",
                                 "contraseña": "123"})
    
    assert response.status_code == 201
    assert partida.get_num_jugadores() == (num_jugadores_viejo + 1)
    assert partida.existe_jugador(partida.get_num_jugadores() - 1)
    assert partida.get_max_jugadores() >= partida.get_num_jugadores()
    player_list = partida.obtener_jugadores()
    nuevo_jugador_presente = False
    for each in player_list:
        nuevo_jugador_presente = nuevo_jugador_presente or (each.get_nombre() == "Brotato")
    assert nuevo_jugador_presente