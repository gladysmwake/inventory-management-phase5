from unittest.mock import patch

import pytest

from inventory_api.errors import ProductNotFoundError, ValidationError
from inventory_api.services import enrich_item
from inventory_api.store import InventoryStore


def test_enrich_keeps_existing_value_when_api_field_is_empty():
    store = InventoryStore()
    product = {"barcode": "5449000000996", "product_name": "Coke", "brands": "", "ingredients_text": ""}
    with patch("inventory_api.services.off_client.fetch_by_barcode", return_value=product):
        item = enrich_item(store, 1)
    assert item["product_name"] == "Coke"
    assert item["brands"] == "Coca-Cola"  # api sent nothing, so it stays


def test_enrich_raises_when_no_barcode():
    store = InventoryStore(items=[{"product_name": "Loose sugar"}])
    with pytest.raises(ValidationError):
        enrich_item(store, 1)


def test_enrich_raises_when_product_unknown():
    store = InventoryStore()
    with patch("inventory_api.services.off_client.fetch_by_barcode", return_value=None):
        with pytest.raises(ProductNotFoundError):
            enrich_item(store, 1)
