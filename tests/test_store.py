import pytest

from inventory_api.errors import ItemNotFoundError
from inventory_api.store import InventoryStore


def test_store_starts_with_seed_items():
    assert len(InventoryStore().all()) == 3


def test_store_can_start_empty():
    assert InventoryStore(items=[]).all() == []


def test_add_assigns_id_and_defaults():
    store = InventoryStore(items=[])
    item = store.add({"product_name": "Rice"})
    assert item["id"] == 1
    assert item["price"] == 0
    assert item["barcode"] == ""


def test_get_missing_item_raises():
    with pytest.raises(ItemNotFoundError):
        InventoryStore().get(999)


def test_update_changes_only_given_fields():
    store = InventoryStore()
    item = store.update(1, {"stock": 7})
    assert item["stock"] == 7
    assert item["product_name"] == "Coca-Cola Original"


def test_delete_removes_item():
    store = InventoryStore()
    store.delete(1)
    with pytest.raises(ItemNotFoundError):
        store.get(1)


def test_ids_are_not_reused():
    store = InventoryStore()
    store.delete(3)
    assert store.add({"product_name": "Honey"})["id"] == 4
