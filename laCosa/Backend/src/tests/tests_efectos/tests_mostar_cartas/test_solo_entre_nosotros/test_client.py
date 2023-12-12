from sseclient import SSEClient
import requests as req
import threading
import sys

def sse_test(player: int):
    # Create a test client

    # Start a thread to listen to the SSE endpoint
    thread = threading.Thread(target=listen_to_sse, args=[player])
    thread.start()

    # Wait for the SSE listener to finish
    thread.join()


def listen_to_sse(player: int):
    # Connect to the SSE endpoint using sseclient-py
    
    sse = SSEClient(f"http://localhost:8000/partidas/0/jugadores/sse/{player}", retry=5)
    
    for event in sse:
        # Process and verify events as they arrive
        event_name = event.event
        event_data = event.data
        if event_name == "Cartas_mostrables":
            print(f"Soy el jugador {player} y recibi un evento:\n")
            print(event_name)
            print(event_data)
        if "Rest in Piss" in event_data:
            break


if __name__ == "__main__":
    sse_test(sys.argv[1])