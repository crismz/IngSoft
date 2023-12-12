import sys
import requests as req

# Caso seduccion sobre jugador en cuarentena
def case_failure():
    response = req.put(url="http://localhost:8000/partidas/0/jugadores/0/jugar", 
                       json={"id_carta": 60, 
                             "id_objetivo": 1})
    assert(response.status_code == 400)

# Caso seducción exitosa
def case_success():
    response = req.put(url="http://localhost:8000/partidas/0/jugadores/0/jugar",
                       json={"id_carta": 60, 
                             "id_objetivo": 2})
    assert(response.status_code == 200)

    response = req.patch(url="http://localhost:8000/partidas/0/jugadores/0/intercambiar", 
                         json={"id_carta" : 100})
    assert response.status_code == 200

    response = req.patch(url="http://localhost:8000/partidas/0/jugadores/2/resolver_intercambio", 
                         json={"id_carta" : 102})
    assert response.status_code == 200


reqs_dict = {"1": case_failure, "2": case_success}

if __name__ == "__main__":
    func = reqs_dict.get(sys.argv[1])
    func()