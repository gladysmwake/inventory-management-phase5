"""The simulated database: a list held in memory.

Everything that touches the list lives in InventoryStore. If this ever moves to
a real database only this file has to change, the routes keep calling the same
methods.
"""
from .errors import ItemNotFoundError

# shaped like what OpenFoodFacts returns, plus our own price and stock
SEED_ITEMS = [
    {"barcode": "5449000000996", "product_name": "Coca-Cola Original", "brands": "Coca-Cola",
     "ingredients_text": "Carbonated water, sugar, colour, acid, flavourings", "price": 1.5, "stock": 40},
    {"barcode": "3017624010701", "product_name": "Nutella", "brands": "Ferrero",
     "ingredients_text": "Sugar, palm oil, hazelnuts, cocoa, skimmed milk powder", "price": 5.25, "stock": 12},
    {"barcode": "0025293000019", "product_name": "Organic Almond Milk", "brands": "Silk",
     "ingredients_text": "Filtered water, almonds, cane sugar", "price": 4.0, "stock": 20},
]

DEFAULTS = {"barcode": "", "product_name": "", "brands": "", "ingredients_text": "", "price": 0, "stock": 0}


class InventoryStore:
    def __init__(self, items=None):
        self._items = []
        self._next_id = 1  # ids only go up, a deleted id is never reused
        for item in (SEED_ITEMS if items is None else items):
            self.add(item)

    def all(self):
        return list(self._items)

    def get(self, item_id):
        for item in self._items:
            if item["id"] == item_id:
                return item
        raise ItemNotFoundError(item_id)

    def add(self, data):
        item = {"id": self._next_id, **DEFAULTS, **data}
        self._next_id += 1
        self._items.append(item)
        return item

    def update(self, item_id, changes):
        item = self.get(item_id)
        item.update(changes)
        return item

    def delete(self, item_id):
        self._items.remove(self.get(item_id))
