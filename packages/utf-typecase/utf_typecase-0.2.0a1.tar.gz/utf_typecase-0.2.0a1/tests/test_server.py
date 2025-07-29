# tests/test_server.py

import pytest
from utf_typecase.server import app, character_store


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_store_and_fetch_character(client):
    token = "test123"
    character_store.clear()

    res = client.post("/send", json={"char": "★", "token": token})
    assert res.get_json()["ok"]

    res = client.get(f"/api/characters?token={token}")
    data = res.get_json()
    assert data["ok"]
    assert data["characters"] == ["★"]

    # Should be empty after fetch
    res = client.get(f"/api/characters?token={token}")
    data = res.get_json()
    assert data["ok"]
    assert data["characters"] == []
    assert "message" in data
