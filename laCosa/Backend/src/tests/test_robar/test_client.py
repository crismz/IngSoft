from fastapi.testclient import TestClient
import sys
sys.path.append("../..")
from main_test import app, lista_partidas

client = TestClient(app)

def test_robo_inicio_turno():
    partida = lista_partidas.get_partida_by_index(0)
    lista_jugadores = partida.obtener_jugadores()
    jugador_0 = lista_jugadores[0]
    largo_mano_viejo = len(jugador_0.get_mano())
    response = client.patch(url="http://localhost:8000/partidas/0/mazo/robar", 
                            json={"id_jugador" : 0, "robo_inicio_turno": True})
    
    assert response.status_code == 200
    assert len(jugador_0.get_mano()) == (largo_mano_viejo + 1)
    return

def test_robo_fuera_turno():
    partida = lista_partidas.get_partida_by_index(0)
    lista_jugadores = partida.obtener_jugadores()
    jugador_0 = lista_jugadores[0]
    cantidad_robos = 2
    jugador_0.set_accion("robos", cantidad_robos)
    largo_mano_viejo = len(jugador_0.get_mano())

    response = client.patch(url="http://localhost:8000/partidas/0/mazo/robar", 
                            json={"id_jugador" : 0, "robo_inicio_turno": False})
    
    assert response.status_code == 200
    assert len(jugador_0.get_mano()) == (largo_mano_viejo + cantidad_robos)
    for each in jugador_0.get_mano():
        assert each.get_type() != "Panico"
    return
