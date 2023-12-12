import requests as req

response = req.put(url=f"http://localhost:8000/partidas/0/jugadores/{1}/jugar", 
                   json={"id_carta" : 108,
                         "id_objetivo": 1})
"""
response = req.put(url=f"http://localhost:8000/partidas/0/jugadores/{1}/revelar", 
                   json={"revela" : True})

response = req.put(url=f"http://localhost:8000/partidas/0/jugadores/{3}/revelar", 
                   json={"revela" : False})

response = req.put(url=f"http://localhost:8000/partidas/0/jugadores/{2}/revelar", 
                   json={"revela" : False})


response = req.put(url=f"http://localhost:8000/partidas/0/jugadores/{2}/revelar", 
                   json={"revela" : True})

response = req.put(url=f"http://localhost:8000/partidas/0/jugadores/{0}/revelar", 
                   json={"revela" : True})
"""