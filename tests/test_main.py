from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_and_get_item():
    create_response = client.post(
        "/items", json={"name": "apple", "price": 1.5}
    )
    assert create_response.status_code == 201
    item_id = create_response.json()["id"]

    get_response = client.get(f"/items/{item_id}")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "apple"


def test_get_missing_item():
    response = client.get("/items/9999")
    assert response.status_code == 404
