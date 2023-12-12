import requests as req


response = req.patch(url="http://localhost:8000/partidas/2/finalizar_turno")
assert response.status_code == 200