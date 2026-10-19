"""In-memory data store for the Inventory Management System.

All database-style operations live here so the route handlers stay thin.
If we ever switch to SQLAlchemy, only this file needs changing.
"""
from .errors import ItemNotFoundError

# Initial seed data modeled after OpenFoodFacts schema plus local pricing and stock
SEED_ITEMS = [
    {
        "barcode": "5449000000996",
        "product_name": "Coca-Cola Original",
        "brands": "Coca-Cola",
        "ingredients_text": "Carbonated water, sugar, colour, acid, flavourings",
        "price": 1.5,
        "stock": 40,
    },
    {
        "barcode": "3017624010701",
        "product_name": "Nutella",
        "brands": "Ferrero",
        "ingredients_text": "Sugar, palm oil, hazelnuts, cocoa, skimmed milk powder",
        "price": 5.25,
        "stock": 12,
    },
    {
        "barcode": "0025293000019",
        "product_name": "Organic Almond Milk",
        "brands": "Silk",
        "ingredients_text": "Filtered water, almonds, cane sugar",
        "price": 4.0,
        "stock": 20,
    },
]

# Baseline dictionary defaults ensuring consistent schema keys for every stored item
DEFAULTS = {
    "barcode": "",
    "product_name": "",
    "brands": "",
    "ingredients_text": "",
    "price": 0,
    "stock": 0,
}


class InventoryStore:
    """Manages the in-memory array of inventory items."""

    def __init__(self, items=None):
        self._items = []
        # IDs always go up — deleted IDs are never reused, just like SQL AUTOINCREMENT
        self._next_id = 1
        for item in (SEED_ITEMS if items is None else items):
            self.add(item)

    def all(self):
        """Return a shallow copy of all inventory items in the store."""
        return list(self._items)

    def get(self, item_id):
        """Retrieve an item by its unique ID or raise ItemNotFoundError (mapped to 404)."""
        for item in self._items:
            if item["id"] == item_id:
                return item
        raise ItemNotFoundError(item_id)

    def add(self, data):
        """Assign the next unique ID, apply baseline schema defaults, and persist to list."""
        item = {"id": self._next_id, **DEFAULTS, **data}
        self._next_id += 1
        self._items.append(item)
        return item

    def update(self, item_id, changes):
        """Apply partial updates to an existing item while preserving untouched fields."""
        item = self.get(item_id)
        item.update(changes)
        return item

    def delete(self, item_id):
        """Remove an item from the list or raise ItemNotFoundError if missing."""
        self._items.remove(self.get(item_id))
