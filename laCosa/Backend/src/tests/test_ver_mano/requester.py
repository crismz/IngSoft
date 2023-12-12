import requests as req
import sys

def mano_jugar_descartar():
    response = req.get(url="http://localhost:8000/jugadores/0/evaluador_mano/Jugar_Descartar")
    assert response.status_code == 200

def mano_descartar():
    response = req.get(url="http://localhost:8000/jugadores/0/evaluador_mano/Descartar")
    assert response.status_code == 200

def mano_intercambiar():
    response = req.get(url="http://localhost:8000/jugadores/0/evaluador_mano/Intercambiar")
    assert response.status_code == 200

def mano_intercambiar_defender():
    response = req.get(url="http://localhost:8000/jugadores/0/evaluador_mano/Intercambiar_Defender")
    assert response.status_code == 200

def mano_esperar():
    response = req.get(url="http://localhost:8000/jugadores/0/evaluador_mano/Esperar")
    assert response.status_code == 200

def mano_defender():
    response = req.get(url="http://localhost:8000/jugadores/0/evaluador_mano/Defender")
    assert response.status_code == 200

def disconnect():
    req.get(url="http://localhost:8000/jugadores/0/evaluador_mano/Close")

reqs_dict = {
    "0": disconnect,
    "1": mano_jugar_descartar,
    "2": mano_descartar,
    "3": mano_intercambiar,
    "4": mano_intercambiar_defender,
    "5": mano_esperar,
    "6": mano_defender
}

if __name__ == "__main__":
    func = reqs_dict.get(sys.argv[1])
    func()
