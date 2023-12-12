import requests as req

base_url = "http://127.0.0.1:8000/"


# Datos correctos
def test_abandona_jugador_cualquiera_lobby():
    params = "partidas/2/jugadores/1"
    url = base_url + params

    response = req.delete(url=url)

    assert response.status_code == 200

def test_abandona_jugador_no_finalizada():
    params = "partidas/3/jugadores/1"
    url = base_url + params

    response = req.delete(url=url)

    assert response.status_code == 422

def test_abandona_jugador_no_existe():
    params = "partidas/2/jugadores/4"
    url = base_url + params

    response = req.delete(url=url)

    assert response.status_code == 404
    assert response.json() == {"detail" : "ID (4) for player Not Found"}

def test_abandona_jugador_no_existe_partida():
    params = "partidas/4/jugadores/1"
    url = base_url + params

    response = req.delete(url=url)

    assert response.status_code == 404
    assert response.json() == {"detail" : "ID (4) for match Not Found"}


def test_abandona_jugador_creador():
    params = "partidas/2/jugadores/0"
    url = base_url + params

    response = req.delete(url=url)

    assert response.status_code == 200

def test_abandona_jugador_creador_finalizada():
    params = "partidas/1/jugadores/0"
    url = base_url + params

    response = req.delete(url=url)

    assert response.status_code == 200

def test_abandona_jugador_finalizada():
    params = "partidas/1/jugadores/2"
    url = base_url + params

    response = req.delete(url=url)

    assert response.status_code == 200