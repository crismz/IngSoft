import sys
sys.path.append("../..")
from fastapi.testclient import TestClient
from sseclient import SSEClient
from main import app  # Import your FastAPI application
import threading

def sse_test(player: int):
    # Create a test client
    client = TestClient(app)
    
    try:
        # Start a thread to listen to the SSE endpoint
        thread = threading.Thread(target=listen_to_sse, args=[player])
        thread.start()

        # Wait for the SSE listener to finish
        thread.join()
    
    except KeyboardInterrupt:
        pass

def listen_to_sse(player: int):
    # Connect to the SSE endpoint using sseclient-py
    
    sse = SSEClient(f"http://127.0.0.1:8000/partidas/0/jugadores/sse/{player}/lobby", retry=5)
    
    for event in sse:
        # Process and verify events as they arrive
        event_name = event.event
        event_data = event.data
        print(event_data)
        if "Rest in piss" in event_name:
            break


if __name__ == "__main__":
    sse_test(sys.argv[1])