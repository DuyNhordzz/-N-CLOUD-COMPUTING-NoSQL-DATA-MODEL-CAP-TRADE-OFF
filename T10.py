import pytest
from fastapi.testclient import TestClient
from app.main import app  # Lâm cung cấp FastAPI app

client = TestClient(app)

def test_01_list_categories():
    r = client.get("/categories")
    assert r.status_code == 200 and isinstance(r.json(), list)

def test_02_create_category_ok():
    r = client.post("/categories", json={"name": "Test Cat", "slug": "test-cat-api"})
    assert r.status_code in (200, 201)

def test_03_create_category_missing_name():
    r = client.post("/categories", json={})
    assert r.status_code == 422

def test_04_create_category_duplicate_slug():
    client.post("/categories", json={"name": "Dup", "slug": "dup-slug"})
    r = client.post("/categories", json={"name": "Dup2", "slug": "dup-slug"})
    assert r.status_code in (400, 409)

def test_05_filter_products_by_category():
    r = client.get("/products", params={"category_id": "any"})
    assert r.status_code == 200 and isinstance(r.json(), list)

def test_06_filter_products_price_range():
    r = client.get("/products", params={"min_price": 10, "max_price": 100})
    assert r.status_code == 200
    for p in r.json():
        assert 10 <= p["price"] <= 100

def test_07_create_product_ok():
    cat = client.post("/categories", json={"name": "C", "slug": "c-for-prod"}).json()
    cid = cat.get("id") or cat.get("_id")
    r = client.post("/products", json={"name": "P", "price": 50, "category_id": cid})
    assert r.status_code in (200, 201)

def test_08_create_product_invalid_category():
    r = client.post("/products", json={"name": "P", "price": 10, "category_id": "ghost"})
    assert r.status_code in (400, 404)

def test_09_create_product_negative_price():
    r = client.post("/products", json={"name": "P", "price": -1, "category_id": "c1"})
    assert r.status_code == 422

def test_10_update_product_price():
    r = client.patch("/products/any-id", json={"price": 999})
    assert r.status_code in (200, 404)  # 404 chấp nhận nếu id không có

def test_11_delete_product():
    r = client.delete("/products/nonexistent")
    assert r.status_code in (204, 404)

def test_12_get_product_not_found():
    r = client.get("/products/definitely-not-exist")
    assert r.status_code == 404
