import sys
import requests as req
import time
from main_test import partida_ejemplo

def case_failure():
    # Caso de alguien que no juega la carta a si mismo
    response = req.put(url="http://localhost:8000/partidas/0/jugadores/0/jugar", 
                       json={"id_carta": 90,
                             "id_objetivo": 1}) 

    assert(response.status_code == 400)


    # Caso de alguien que no tiene la carta
    response = req.put(url="http://localhost:8000/partidas/0/jugadores/1/jugar", 
                       json={"id_carta": 90, 
                             "id_objetivo": 1})

    assert(response.status_code == 404)


def case_success():
    # Caso exitoso
    response = req.put(url="http://localhost:8000/partidas/0/jugadores/0/jugar",
                       json={"id_carta": 90, 
                             "id_objetivo": 0})

    #assert(response.status_code == 200)
    print(response.json())

reqs_dict = {"1": case_failure, "2": case_success}

if __name__ == "__main__":
    func = reqs_dict.get(sys.argv[1])
    func()