from unittest.mock import patch

from inventory_api.errors import ExternalAPIError

FAKE_PRODUCT = {
    "barcode": "3017624010701",
    "product_name": "Nutella 400g",
    "brands": "Ferrero",
    "ingredients_text": "Sugar, palm oil, hazelnuts",
}


# ---------- GET ----------

def test_get_all_items(client):
    res = client.get("/inventory")
    assert res.status_code == 200
    assert len(res.get_json()) == 3


def test_get_single_item(client):
    res = client.get("/inventory/3")
    assert res.status_code == 200
    assert res.get_json()["product_name"] == "Organic Almond Milk"


def test_get_missing_item_returns_404(client):
    res = client.get("/inventory/999")
    assert res.status_code == 404
    assert "error" in res.get_json()


# ---------- POST ----------

def test_add_item(client):
    res = client.post("/inventory", json={"product_name": "Peanut Butter", "price": 3.5, "stock": 8})
    assert res.status_code == 201
    created = res.get_json()
    assert created["id"] == 4
    assert created["stock"] == 8
    assert len(client.get("/inventory").get_json()) == 4


def test_add_item_defaults(client):
    body = client.post("/inventory", json={"product_name": "Water"}).get_json()
    assert body["price"] == 0
    assert body["stock"] == 0
    assert body["barcode"] == ""


def test_add_item_without_name_fails(client):
    assert client.post("/inventory", json={"price": 2}).status_code == 400


def test_add_item_bad_price_fails(client):
    assert client.post("/inventory", json={"product_name": "Rice", "price": -4}).status_code == 400


def test_add_item_without_json_fails(client):
    res = client.post("/inventory", data="not json", content_type="text/plain")
    assert res.status_code == 400


# ---------- PATCH ----------

def test_patch_price_and_stock(client):
    res = client.patch("/inventory/1", json={"price": 2.0, "stock": 5})
    assert res.status_code == 200
    item = res.get_json()
    assert item["price"] == 2.0
    assert item["stock"] == 5
    assert item["product_name"] == "Coca-Cola Original"  # untouched


def test_patch_missing_item_returns_404(client):
    assert client.patch("/inventory/999", json={"price": 1}).status_code == 404


def test_patch_invalid_value_returns_400(client):
    assert client.patch("/inventory/1", json={"stock": -1}).status_code == 400


# ---------- DELETE ----------

def test_delete_item(client):
    assert client.delete("/inventory/2").status_code == 200
    assert client.get("/inventory/2").status_code == 404
    assert len(client.get("/inventory").get_json()) == 2


def test_delete_missing_item_returns_404(client):
    assert client.delete("/inventory/999").status_code == 404


# ---------- OpenFoodFacts routes (external calls are mocked) ----------

def test_lookup_barcode(client):
    with patch("inventory_api.routes.off_client.fetch_by_barcode", return_value=FAKE_PRODUCT):
        res = client.get("/lookup/barcode/3017624010701")
    assert res.status_code == 200
    assert res.get_json()["brands"] == "Ferrero"


def test_lookup_barcode_not_found(client):
    with patch("inventory_api.routes.off_client.fetch_by_barcode", return_value=None):
        assert client.get("/lookup/barcode/123").status_code == 404


def test_lookup_barcode_rejects_letters(client):
    assert client.get("/lookup/barcode/abc").status_code == 400


def test_lookup_search(client):
    with patch("inventory_api.routes.off_client.search_by_name", return_value=[FAKE_PRODUCT]):
        res = client.get("/lookup/search?name=nutella")
    assert res.status_code == 200
    assert len(res.get_json()) == 1


def test_lookup_search_needs_name(client):
    assert client.get("/lookup/search").status_code == 400


def test_enrich_item_updates_details(client):
    with patch("inventory_api.services.off_client.fetch_by_barcode", return_value=FAKE_PRODUCT):
        res = client.post("/inventory/2/enrich")
    assert res.status_code == 200
    item = res.get_json()
    assert item["product_name"] == "Nutella 400g"
    assert item["price"] == 5.25  # our own data is kept
    assert item["stock"] == 12


def test_enrich_item_without_barcode(client):
    item_id = client.post("/inventory", json={"product_name": "Loose sugar"}).get_json()["id"]
    assert client.post(f"/inventory/{item_id}/enrich").status_code == 400
