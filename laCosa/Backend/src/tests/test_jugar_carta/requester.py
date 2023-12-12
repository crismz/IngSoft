import sys
import requests as req

jugar_partida_equivocada = "http://127.0.0.1:8000/partidas/43/jugadores/0/jugar"
jugar_jugador_equivocado = "http://127.0.0.1:8000/partidas/0/jugadores/43/jugar"
defender_partida_equivocada = "http://127.0.0.1:8000/partidas/43/jugadores/0/defensa"
defender_jugador_equivocado = "http://127.0.0.1:8000/partidas/0/jugadores/43/defensa"

body_objetivo_equivocado = {
    "id_carta": 22,
    "id_objetivo": 43
}

body_carta_equivocada = {
    "id_carta": 800,
    "id_objetivo": 1
}

body_mala_jugada_carta = {
    "id_objetivo": 1
}

body_mala_jugada_objetivo = {
    "id_carta": 200
}

body_mala_defensa = {
    "id_carta_de_defensa": -300
}

jugar = "http://127.0.0.1:8000/partidas/0/jugadores/0/jugar"
defender = "http://127.0.0.1:8000/partidas/0/jugadores/1/defensa"

body_lanzallamas = {
    "id_carta": 22,
    "id_objetivo": 1
}

body_extintor = {
    "id_carta": 82
}

body_no_defense = {
    "id_carta": -1
}

body_indefendible = {
    "id_carta": 200,
    "id_objetivo": 1
}


def case_jugar_partida_equivocada():
    response = req.put(url=jugar_partida_equivocada, 
                         json=body_lanzallamas)
    assert response.status_code == 404
    print("case_jugar_partida_equivocada passed")

def case_jugar_jugador_equivocado():
    response = req.put(url=jugar_jugador_equivocado, 
                         json=body_lanzallamas)
    assert response.status_code == 404
    print("case_jugar_jugador_equivocado passed")

def case_mala_jugada_objetivo():
    response = req.put(url=jugar, 
                         json=body_mala_jugada_objetivo)
    assert response.status_code == 422
    print("case_mala_jugada_objetivo passed")

def case_mala_jugada_carta():
    response = req.put(url=jugar, 
                         json=body_mala_jugada_carta)
    assert response.status_code == 422
    print("case_mala_jugada_carta passed")

def case_jugar_objetivo_equivocado():
    response = req.put(url=jugar, 
                         json=body_objetivo_equivocado)
    assert response.status_code == 404
    print("case_jugar_objetivo_equivocado passed")

def case_jugar_carta_equivocada():
    response = req.put(url=jugar, 
                         json=body_carta_equivocada)
    assert response.status_code == 404
    print("case_jugar_carta_equivocada passed")

def case_defender_partida_equivocada():
    response = req.put(url=defender_partida_equivocada, 
                         json=body_extintor)
    assert response.status_code == 404
    print("case_defender_partida_equivocada passed")

def case_defender_jugador_equivocado():
    response = req.put(url=defender_jugador_equivocado, 
                         json=body_extintor)
    assert response.status_code == 404
    print("case_defender_jugador_equivocado passed")

def case_mala_defensa():
    response = req.put(url=defender, 
                         json=body_mala_defensa)
    assert response.status_code == 422
    print("case_mala_defensa passed")

def cases_of_failure():
    print("\n\nRunning testcases of failure...\n\n")
    case_jugar_partida_equivocada()
    case_jugar_jugador_equivocado()
    case_mala_jugada_objetivo()
    case_mala_jugada_carta()
    case_jugar_objetivo_equivocado()
    case_jugar_carta_equivocada()
    case_defender_partida_equivocada()
    case_defender_jugador_equivocado()
    case_mala_defensa()
    print("\n\nTestcases of failure passed!\n\n")
          
def case_no_defense():
    print("\n\nRunning testcase of the objecitve not defending...\n\n")
    response = req.put(url=jugar, 
                         json=body_lanzallamas)
    assert response.status_code == 200

    response = req.put(url=defender, 
                         json=body_no_defense)
    assert response.status_code == 200
    print("\n\nTestcase of the objective not defending passed!\n\n")

def case_defense():
    print("\n\nRunning testcase of defensible card mecanics...\n\n")
    response = req.put(url=jugar, 
                         json=body_lanzallamas)
    assert response.status_code == 200

    response = req.put(url=defender, 
                         json=body_extintor)
    assert response.status_code == 200
    print("\n\nTestcase of defensible card mecanics passed!\n\n")

def indefensible_case():
    print("\n\nRunning testcase of indefensible card mecanics...\n\n")
    response = req.put(url=jugar, 
                         json=body_indefendible)
    assert response.status_code == 200
    print("\n\nTestcase of indefensible card mecanics passed!\n\n")

# Cada case del requester DEBE correrse con un server independiente

reqs_dict = {
    "0": cases_of_failure,
    "1": case_no_defense,
    "2": case_defense,
    "3": indefensible_case
}

if __name__ == "__main__":
    func = reqs_dict.get(sys.argv[1])
    func()
