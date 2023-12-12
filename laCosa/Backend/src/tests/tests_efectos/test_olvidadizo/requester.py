import requests as req

jugar_olvidadizo="http://127.0.0.1:8000/partidas/0/jugadores/0/jugar"
body_olvidadizo={
  "id_carta": 98,
  "id_objetivo": 0
}

response_play = {
    "robos": 3,
    "descartes": 3,
    "intercambios": 1
}

response_fst_discard = {
    "robos": 3,
    "descartes": 2,
    "intercambios": 1
}

response_snd_discard = {
    "robos": 3,
    "descartes": 1,
    "intercambios": 1
}

response_thrd_discard = {
    "robos": 0,
    "descartes": 0,
    "intercambios": 1
}

descartar = "http://127.0.0.1:8000/partidas/0/jugadores/0/descartar?id_carta="


# Caso jugada fuera de intercambio
def request():
    response = req.put(url=jugar_olvidadizo, 
                         json=body_olvidadizo)
    assert response.status_code == 200
    assert response.json() == response_play
    print("Olvidadizo card played successfully")

    response = req.patch(url=descartar+"400")
    assert response.status_code == 200
    assert response.json() == response_fst_discard
    print("First card discarded successfully")

    response = req.patch(url=descartar+"401")
    assert response.status_code == 200
    assert response.json() == response_snd_discard
    print("Second card discarded successfully")

    response = req.patch(url=descartar+"402")
    assert response.status_code == 200
    assert response.json() == response_thrd_discard
    print("Third card discarded successfully")
    print("All 3 cards stolen successfully")

if __name__ == "__main__":
    request()