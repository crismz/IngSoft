from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
expected_pocos = {
    "nombre_partida" : "LasAventurasDelCapitanHatteras",
    "min_jugadores": 4,
    "max_jugadores": 4
}
expected_muchos= {
    "nombre_partida" : "LaSombraSobreInnsmouth",
    "min_jugadores": 4,
    "max_jugadores": 12
}
# Partida inexistente
def test_partida_inexistente():
    response = client.get(url="/64")
    assert response.status_code == 404

# Pocos jugadores
def test_pocos_jugadores():
    response = client.get(url="/0")
    assert response.status_code == 200
    assert response.json() == expected_pocos

# Muchos jugadores
def test_muchos_jugadores():
    response = client.get(url="/1")
    assert response.status_code == 200
    assert response.json() == expected_muchos