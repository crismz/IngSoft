import requests as r

response = r.get('http://localhost:8000/')
print(response.json())