from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_frontend_root_available():
    response = client.get("/")
    assert response.status_code == 200
    assert "Robo QI" in response.text


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_connect_requires_valid_gmail_and_password():
    response = client.post("/connect", json={"gmail": "naogmail@outlook.com", "senha": "12345678"})
    assert response.status_code == 400

    response2 = client.post("/connect", json={"gmail": "user@gmail.com", "senha": "123"})
    assert response2.status_code == 422


def test_create_and_cancel_order_flow():
    c = client.post("/connect", json={"gmail": "operador@gmail.com", "senha": "senhaforte123"})
    assert c.status_code == 200

    r = client.post(
        "/orders",
        json={"symbol": "EURUSD", "side": "buy", "amount": 25, "expiration_seconds": 60},
    )
    assert r.status_code == 200
    order = r.json()["order"]
    assert order["symbol"] == "EURUSD"

    get_order = client.get(f"/orders/{order['id']}")
    assert get_order.status_code == 200

    cancel = client.post(f"/orders/{order['id']}/cancel")
    assert cancel.status_code == 200
    assert cancel.json()["order"]["status"] in {"canceled", "executed", "rejected"}


def test_order_requires_connection():
    client.post("/disconnect")
    r = client.post(
        "/orders",
        json={"symbol": "EURUSD", "side": "sell", "amount": 10, "expiration_seconds": 60},
    )
    assert r.status_code == 409
