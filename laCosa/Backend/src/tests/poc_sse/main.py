from fastapi import FastAPI, Request, HTTPException
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
import sys
sys.path.append("../..")
import asyncio
from collections import defaultdict


app = FastAPI()

conexiones = defaultdict(list)

class CardPlay(BaseModel):
    carta: str
    source: str
    id_jugador: int

async def event_sender(id_jugador: int):
    try:
        while True:
            if id_jugador in conexiones and len(conexiones[id_jugador]) > 0:
                #yield conexiones[id_jugador].pop()
                response = conexiones[id_jugador].pop()
                print(response)
                yield response
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        print(f"El jugador {id_jugador} metió el router al microondas")
    except Exception as e:
        print(f"Hubo problemas con el jugador {id_jugador}: {e}")
    finally:
        del conexiones[id_jugador]

# Endpoint que crea y hace handle de las conexiones SSE
@app.get("/subscribe/{id_jugador}", status_code= 200)
async def sse_endpoint(id_jugador: int, req: Request):
    try:
        #Falta chequear que la partida existe, que el jugador está en ella, etc..
        if id_jugador not in conexiones:
            conexiones[id_jugador] = []
        return EventSourceResponse(event_sender(id_jugador))
        #Falta hacer algo con la response cuando llega
    except Exception as e:
        print("El server chocó con un cactus!")
        print("{e}")
        raise HTTPException(status_code=500, detail="El server se cayó del caballo...")
        

@app.post("/play/{id_jugador}", status_code= 200)
async def jugada(id_jugador: int, jugadihna: CardPlay):
    #Falta chequear que la partida existe
    try:
        if id_jugador not in conexiones:
            raise HTTPException(status_code=400, detail="No estás suscrito al canal!")
        if jugadihna.id_jugador not in conexiones:
            raise HTTPException(status_code=400, detail="Ese jugador no está suscrito al canal!")
        
        conexiones[jugadihna.id_jugador].append(jugadihna)
        return {"Message": jugadihna.carta + " Played!"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Tu carta se cayó por un barranco")
        print(f"El barranco en cuestión: {e}")
        raise HTTPException(status_code=500, detail="El server se cayó del caballo...")