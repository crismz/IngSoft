import sys
sys.path.append("../..")
import requests

"""
Endpoint hecho para testear

async def obtener_partida(id_partida:int) -> Partida:
    if id_partida == 0:
        part = lista_partidas.get_partida_by_index(lista_partidas.get_index_by_id(id_partida))
        if  (part.nombre == "partidita" and 
        part.id == 1 and
        part.contraseña == "" and
        part.max_jugadores == 12 and
        part.min_jugadores == 4 and
        part.iniciada == False and
        part.buscar_jugador(0).get_nombre() == "pepito"):
            return part
    
    else: 
        part = lista_partidas.get_partida_by_index(lista_partidas.get_index_by_id(id_partida))
        if  (part.nombre == "partidita2" and 
        part.id == 2 and
        part.contraseña == "pepito" and
        part.max_jugadores == 10 and
        part.min_jugadores == 6 and
        part.iniciada == False and
        part.buscar_jugador(0).get_nombre() == "pep ito2"):
            return part  
        
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
"""

def test_crear_partida():
    url="http://127.0.0.1:8000/partidas/crear"
    data ={        
        "nombre_partida": "partidita",
        "contraseña": "",
        "max_jugadores": 12,
        "min_jugadores": 4,
        "nombre_jugador": "pepito"
    }

    response = requests.post(url,json=data)

    assert response.status_code == 201
    
    partida = requests.get(f"http://127.0.0.1:8000/partidas/{response.json()['id_partida']}")

    assert partida.status_code == 200
    

def test_crear_partida2():
    url="http://127.0.0.1:8000/partidas/crear"
    data = {        
        "nombre_partida": "    partidita2    ",
        "contraseña": "pepito",
        "max_jugadores": 10,
        "min_jugadores": 6,
        "nombre_jugador": "pep   ito2"
    }

    response = requests.post(url,json=data)

    from partidas.endpoints import lista_partidas

    assert response.status_code == 201

    partida = requests.get(f"http://127.0.0.1:8000/partidas/{response.json()['id_partida']}")

    assert partida.status_code == 200



def test_crear_partidatoolong():
    url="http://127.0.0.1:8000/partidas/crear"
    data = {        
        "nombre_partida": "partiditksaljdklasjdlksajdklsadjklasjdklsajklasjdklasjdklsajljdklsajdkasjlkdjklasdjklasa",
        "contraseña": "",
        "max_jugadores": 4,
        "min_jugadores": 12,
        "nombre_jugador": "pepito"
    }

    response = requests.post(url,json=data)
    assert response.status_code == 400

def test_crear_partidaempty():
    url="http://127.0.0.1:8000/partidas/crear"
    data = {        
        "nombre_partida": "",
        "contraseña": "",
        "max_jugadores": 4,
        "min_jugadores": 12,
        "nombre_jugador": "pepito"
    }
    response = requests.post(url,json=data)
    assert response.status_code == 400


def test_crear_partidapassmal():
    url="http://127.0.0.1:8000/partidas/crear"
    data = {        
        "nombre_partida": "partidita",
        "contraseña": "a b",
        "max_jugadores": 4,
        "min_jugadores": 12,
        "nombre_jugador": "pepito"
    }
    response = requests.post(url,json=data)
    assert response.status_code == 400



def test_crear_partidamaljug():
    url="http://127.0.0.1:8000/partidas/crear"
    data = {        
        "nombre_partida": "partidita",
        "contraseña": "ab",
        "max_jugadores": 2,
        "min_jugadores": 12,
        "nombre_jugador": "juan@"
    }
    response = requests.post(url,json=data)
    assert response.status_code == 400


def test_crear_partidamaljug2():
    url="http://127.0.0.1:8000/partidas/crear"
    data = {        
        "nombre_partida": "partidita",
        "contraseña": "ab",
        "max_jugadores": 6,
        "min_jugadores": 8,
        "nombre_jugador": "pedro&"
    }
    response = requests.post(url,json=data)
    assert response.status_code == 400
