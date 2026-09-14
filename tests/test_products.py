import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.product import Product  # noqa: F401  (registers table on Base metadata)

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def _reset_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_create_product():
    response = client.post(
        "/products",
        json={
            "name": "ワイヤレスイヤホン",
            "rating": 5,
            "comments": [{"user": "alice", "text": "最高でした"}],
            "category": "家電",
            "stock_quantity": 10,
            "price": 3980,
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["product_id"] == 1
    assert body["name"] == "ワイヤレスイヤホン"
    assert body["rating"] == 5
    assert body["comments"] == [{"user": "alice", "text": "最高でした"}]
    assert body["category"] == "家電"
    assert body["stock_quantity"] == 10
    assert body["price"] == 3980


def test_create_product_rejects_out_of_range_rating():
    response = client.post(
        "/products",
        json={
            "name": "テスト商品",
            "rating": 6,
            "comments": [],
            "category": "その他",
            "stock_quantity": 1,
            "price": 100,
        },
    )

    assert response.status_code == 422


def test_list_and_get_product():
    create_response = client.post(
        "/products",
        json={
            "name": "マグカップ",
            "rating": 3,
            "comments": [],
            "category": "キッチン用品",
            "stock_quantity": 20,
            "price": 1200,
        },
    )
    product_id = create_response.json()["product_id"]

    list_response = client.get("/products")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    get_response = client.get(f"/products/{product_id}")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "マグカップ"


def test_get_product_not_found():
    response = client.get("/products/999")
    assert response.status_code == 404


def test_delete_product():
    create_response = client.post(
        "/products",
        json={
            "name": "削除対象",
            "rating": 1,
            "comments": [],
            "category": "その他",
            "stock_quantity": 0,
            "price": 500,
        },
    )
    product_id = create_response.json()["product_id"]

    delete_response = client.delete(f"/products/{product_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/products/{product_id}")
    assert get_response.status_code == 404
