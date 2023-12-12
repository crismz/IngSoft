from fastapi.testclient import TestClient
from main import app, lista_jugadores

client = TestClient(app)

except_kelsier = []
except_kelsier_and_dupin = []

for each in lista_jugadores:
    nombre = each.get_nombre()

    if nombre != "Kelsier":
        except_kelsier.append({"name" : nombre})

    if nombre != "Kelsier" and nombre != "C. Auguste Dupin":
        except_kelsier_and_dupin.append({"name" : nombre}) 

expected_one_change={
    "jugadores" : except_kelsier
}

expected_two_changes ={
    "jugadores": except_kelsier_and_dupin
}

# Uso del lanzallamas sobre uno mismo
def test_quemar_self():
    response = client.get("/0/quemar/0/0/22")
    assert response.status_code == 400

# Uso del lanzallamas sobre un jugador no adyacente
def test_quemar_no_adyacente():
    response = client.get("/0/quemar/0/2/22")
    assert response.status_code == 400

# Usar un lanzallamas sobre un jugador bloqueado a izquierda
def test_quemar_bloqueado_izquierda():
    response = client.get("/0/quemar/0/1/22")
    assert response.status_code == 400

# Usar un lanzallamas sobre un jugador bloqueado a derecha
def test_quemar_bloqueado_derecha():
    response = client.get("/0/quemar/2/1/24")
    assert response.status_code == 400

# Usar un lanzallamas sobre un jugador válido para ello a derecha
def test_quemar_valido_derecha():
    response = client.get("/0/quemar/0/3/22")
    assert response.status_code == 200
    assert response.json() == expected_one_change

# Usar un lanzallamas sobre un jugador válido para ello a izquierda
def test_quemar_valido_izquierda():
    response = client.get("/0/quemar/2/0/24")
    assert response.status_code == 200
    assert response.json() == expected_two_changes