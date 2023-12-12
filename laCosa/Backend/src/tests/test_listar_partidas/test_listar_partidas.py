import requests as req

base_url = "http://127.0.0.1:8000/"


def test():
    params = "partidas"
    url = base_url + params

    response = req.get(url=url)

    listado = response.json()['lista']

    assert response.status_code == 200
    assert len(listado) == 4
    assert listado[0]['id_partida'] == 2
    assert listado[0]['nombre_partida'] == "patito"
    assert listado[0]['jugadores_act'] == 4
    assert listado[0]['max_jugadores'] == 6
    assert listado[0]['tiene_contraseña'] == True
    assert listado[1]['id_partida'] == 3
    assert listado[2]['id_partida'] == 4
    assert listado[3]['id_partida'] == 5
    assert listado[3]['nombre_partida'] == "patito4"
    assert listado[3]['max_jugadores'] == 12
    assert listado[3]['jugadores_act'] == 6
    assert listado[3]['tiene_contraseña'] == False