# tests/test_client.py

import time


def test_callback_called(monkeypatch):
    # Simulate receiving a character list
    test_output = []

    def mock_get(*args, **kwargs):
        class Response:
            def raise_for_status(self):
                pass

            def json(self):
                return {"ok": True, "characters": ["✓"]}

        return Response()

    monkeypatch.setattr("requests.get", mock_get)

    from utf_typecase.client import UTFClient

    def callback(chars):
        test_output.extend(chars)

    client = UTFClient("http://localhost:5000", "test123", interval_ms=100)
    client.on_data(callback)
    client.start()
    time.sleep(0.2)
    client.stop()

    assert "✓" in test_output
