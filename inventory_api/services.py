"""Logic that combines the store and OpenFoodFacts, so routes can stay thin."""
from . import off_client
from .errors import ProductNotFoundError, ValidationError

ENRICHABLE_FIELDS = ("product_name", "brands", "ingredients_text")


def enrich_item(store, item_id):
    """Fill in an item's details from OpenFoodFacts using its barcode.

    Only fields OpenFoodFacts actually has are overwritten. Our own price and
    stock are never touched.
    """
    item = store.get(item_id)
    if not item["barcode"]:
        raise ValidationError("this item has no barcode to look up")

    product = off_client.fetch_by_barcode(item["barcode"])
    if product is None:
        raise ProductNotFoundError(item["barcode"])

    changes = {key: product[key] for key in ENRICHABLE_FIELDS if product[key]}
    return store.update(item_id, changes)
