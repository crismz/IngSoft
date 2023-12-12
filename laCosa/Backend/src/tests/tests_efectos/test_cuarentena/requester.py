import sys
import requests as req
import time
from main_test import partida_ejemplo

def case_failure():
    # Caso de alguien que juega la carta a si mismo
    response = req.put(url="http://localhost:8000/partidas/0/jugadores/0/jugar", 
                       json={"id_carta": 84,
                             "id_objetivo": 0}) 

    assert(response.status_code == 400)


    # Caso de alguien que no tiene la carta
    response = req.put(url="http://localhost:8000/partidas/0/jugadores/1/jugar", 
                       json={"id_carta": 84, 
                             "id_objetivo": 1})

    assert(response.status_code == 404)


def case_success():
    # Caso exitoso
    response = req.put(url="http://localhost:8000/partidas/0/jugadores/0/jugar",
                       json={"id_carta": 84, 
                             "id_objetivo": 1})

    assert(response.status_code == 200)

def case_quarantine_is_over():
    for _ in range(partida_ejemplo.get_num_jugadores() * 3):
        response = req.patch(url=f"http://localhost:8000/partidas/{partida_ejemplo.get_id()}/finalizar_turno")
        #assert response.status_code == 200

reqs_dict = {"1": case_failure, "2": case_success, "3": case_quarantine_is_over}

if __name__ == "__main__":
    func = reqs_dict.get(sys.argv[1])
    func()