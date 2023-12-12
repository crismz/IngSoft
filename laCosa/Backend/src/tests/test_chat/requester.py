import requests as req

response = req.post(url="http://localhost:8000/partidas/0/chat", 
                    json={"id_jugador" : 0, 
                          "mensaje": "How did I end up here?"})
assert response.status_code == 200
