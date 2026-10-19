"""Service layer bridging the internal inventory store and external OpenFoodFacts integration.

Encapsulates data orchestration and domain logic away from HTTP request handlers.
"""
from . import off_client
from .errors import ProductNotFoundError, ValidationError

# Domain fields that can be safely enriched from external metadata
ENRICHABLE_FIELDS = ("product_name", "brands", "ingredients_text")


def enrich_item(store, item_id):
    """Pull product details from OpenFoodFacts and update a stored item.

    The item needs a barcode to look anything up. Only non-empty fields
    (product_name, brands, ingredients_text) get overwritten; price, stock
    and id are never touched.
    """
    item = store.get(item_id)
    if not item["barcode"]:
        raise ValidationError("this item has no barcode to look up")

    product = off_client.fetch_by_barcode(item["barcode"])
    if product is None:
        raise ProductNotFoundError(item["barcode"])

    # Only overwrite attributes that actually returned non-empty values from the external API
    changes = {key: product[key] for key in ENRICHABLE_FIELDS if product[key]}
    return store.update(item_id, changes)
