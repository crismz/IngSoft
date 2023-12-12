from sseclient import SSEClient
import sys


def listen_to_sse(player: int):
    # Connect to the SSE endpoint using sseclient-py
    sse = SSEClient(f"http://localhost:8000/partidas/0/jugadores/sse/{player}", retry=5)
    
    for event in sse:
        # Process and verify events as they arrive
        event_name = event.event
        event_data = event.dump()
        if event_name != "message":
            print(event_name)
            print(event_data)
        if event_name == "Fin":
            break

if __name__ == "__main__":
    listen_to_sse(sys.argv[1])