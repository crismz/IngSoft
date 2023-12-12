from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_hub():
    response = client.get("/")
    assert response.status_code == 200
    return

def test_id_inexistente():
    response = client.patch("partidas/20/finalizar_turno")
    assert response.status_code == 404
    return

def test_no_iniciada():
    response = client.patch("partidas/0/finalizar_turno")
    assert response.status_code == 422
    return

def test_clockwise():
    response = client.patch("partidas/1/finalizar_turno")
    assert response.status_code == 200
    return

def test_counter_clockwise():
    response = client.patch("partidas/2/finalizar_turno")
    assert response.status_code == 200
    return

def test_clockwise_borde():
    response = client.patch("partidas/3/finalizar_turno")
    assert response.status_code == 200
    return


def test_counter_clockwise_borde():
    response = client.patch("partidas/4/finalizar_turno")
    assert response.status_code == 200
    return