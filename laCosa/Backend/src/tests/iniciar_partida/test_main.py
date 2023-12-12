from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Partida inexistente
def test_partida_inexistente():
    response = client.patch(
        url="/64/iniciar",
        json={
                "id_jugador": 3,
            })
    print(response.json())
    assert response.status_code == 404

# Jugador inválido
def test_jugador_inválido():
    response = client.patch(
        "/0/iniciar",
        json={
                "id_jugador": 3,
            })
    print(response)
    assert response.status_code == 422

# Jugadores insuficientes
def test_jugadores_insuficientes():
    response = client.patch(
        "/0/iniciar",
        json={
                "id_jugador": 0,
            })
    print(response)
    assert response.status_code == 400

# Partida ya iniciada
def test_partida_ya_iniciada():
    response = client.patch(
        "/1/iniciar",
        json={
                "id_jugador": 0,
            })
    print(response)
    assert response.status_code == 422

# Partida válida
def test_partida_valida():
    response = client.patch(
        "/2/iniciar",
        json={
                "id_jugador": 0,
            })
    print(response)
    assert response.status_code == 200
    response = client.patch(
        "/2/iniciar",
        json={
                "id_jugador": 0,
            })
    print(response)
    assert response.status_code == 422