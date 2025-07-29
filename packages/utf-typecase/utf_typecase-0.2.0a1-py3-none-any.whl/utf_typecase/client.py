# utf_typecase/client.py

import time
import threading
import requests


class UTFClient:
    def __init__(self, server_url, token, interval_ms=250):
        self.server_url = server_url.rstrip("/")
        self.token = token
        self.interval = interval_ms / 1000.0
        self.callback = None
        self._running = False

    def on_data(self, func):
        """Registers a function to be called with new character data."""
        self.callback = func

    def start(self):
        """Starts polling the server in a background thread."""
        if not self.callback:
            raise ValueError("No callback registered with on_data()")
        self._running = True
        threading.Thread(target=self._poll, daemon=True).start()

    def stop(self):
        """Stops the polling loop."""
        self._running = False

    def _poll(self):
        while self._running:
            try:
                url = f"{self.server_url}/api/characters"
                response = requests.get(url, params={"token": self.token})
                response.raise_for_status()
                payload = response.json()
                if payload.get("ok") and payload.get("characters"):
                    self.callback(payload["characters"])
            except Exception as e:
                print(f"[CLIENT] Poll error: {e}")
            time.sleep(self.interval)


# For quick testing: run with 'python src/utf_typecase/client.py'
if __name__ == "__main__":

    def show_characters(chars):
        print("[CLIENT] Received:", "".join(chars))

    client = UTFClient(
        server_url="http://localhost:5000", token="dev123", interval_ms=250
    )
    client.on_data(show_characters)
    client.start()

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n[CLIENT] Stopping...")
        client.stop()
