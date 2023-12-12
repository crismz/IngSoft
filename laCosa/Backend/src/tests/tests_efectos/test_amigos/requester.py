import sys
import requests as req

# Caso Amigos sobre jugador en cuarentena
def case_failure():
    response = req.put(url="http://localhost:8000/partidas/0/jugadores/0/jugar", 
                       json={"id_carta": 101, 
                             "id_objetivo": 1})
    assert(response.status_code == 400)
    print("'Why can't we be friends?' quarantine case tested successfully")



# Caso Amigos exitoso
def case_success():
    response = req.put(url="http://localhost:8000/partidas/0/jugadores/0/jugar",
                       json={"id_carta": 101, 
                             "id_objetivo": 2})
    assert(response.status_code == 200)
    print("'Why can't we be friends?' played successfully")

    response = req.patch(url="http://localhost:8000/partidas/0/jugadores/0/intercambiar", 
                         json={"id_carta" : 100})
    assert response.status_code == 200
    print("First phase of 'Why can't we be friends?' exchange successful")

    response = req.patch(url="http://localhost:8000/partidas/0/jugadores/2/resolver_intercambio", 
                         json={"id_carta" : 104})
    assert response.status_code == 200
    print("Second phase of 'Why can't we be friends?' exchange successful")
    print("'Why can't we be friends?' exchange completed successfully")

    response = req.patch(url="http://localhost:8000/partidas/0/jugadores/0/intercambiar", 
                         json={"id_carta" : 106})
    assert response.status_code == 200
    print("First phase of regular exchange successful")

    response = req.patch(url="http://localhost:8000/partidas/0/jugadores/1/resolver_intercambio", 
                         json={"id_carta" : 103})
    assert response.status_code == 200
    print("Second phase of regular exchange successful")
    print("Regular exchange completed successfully")


reqs_dict = {"0": case_failure, "1": case_success}

if __name__ == "__main__":
    func = reqs_dict.get(sys.argv[1])
    func()