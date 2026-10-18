"""Simulated in-memory database store for the Inventory Management System.

Architectural Pattern: Repository / Data Store
All persistence operations are encapsulated inside `InventoryStore`. The Flask route
handlers only interact with this abstraction. If migrating to SQLAlchemy/PostgreSQL,
only this class interface needs to be rewritten, leaving HTTP controllers untouched.
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
        # Monotonically increasing primary key counter. Deleted IDs are never recycled,
        # mirroring the behavior of AUTOINCREMENT in relational database engines.
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
