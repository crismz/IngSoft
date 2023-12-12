import asyncio
import httpx
from httpx_sse import aconnect_sse
from sse_starlette.sse import EventSourceResponse

mano = ["Lanzallamas", "Extintor", "Blank", "Blank"]

async def subscribe_to_sse(client, id_jugador):
    print(id_jugador)
    async with aconnect_sse(client, "GET", f"http://localhost:8000/subscribe/{id_jugador}", timeout=120) as event_source:
        async for sse in event_source.aiter_sse():
            if "Lanzallamas" in sse.data:
                print("Un jugador quiere quemarte con el Lanzallamas!!!")
                if "Extintor" in mano:
                    print("... pero no contaba con tu Extintor!")
                    mano.remove("Extintor")
                    print("Exitintor descartado")
                else:
                    print("..y no tenías como defenderte :(")

                

async def main():
    async with httpx.AsyncClient() as client:
        # Subscribe to SSE for id_jugador 0
        await subscribe_to_sse(client, 1)

    #response = await client.post("http://localhost:8000/play/0/", json={"carta": "Lanzallamas", "source": "Patito", "id_jugador": 0})
    #print("POST response:", response.status_code, response.json())

if __name__ == "__main__":
    asyncio.run(main())