import requests as req

"""
response = req.put(url=f"http://localhost:8000/partidas/0/jugadores/{1}/jugar", 
                   json={"id_carta" : 1,
                         "id_objetivo": 2})

"""
"""
response2 = req.put(url=f"http://localhost:8000/partidas/0/jugadores/{3}/defensa", 
                   json={"id_carta" : 1})

"""

response2 = req.patch(url=f"http://localhost:8000/partidas/0/jugadores/{2}/intercambiar", 
                   json={"id_carta" : 1})

