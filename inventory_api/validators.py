"""Input validation for inventory items. Raises ValidationError on bad input."""
from .errors import ValidationError

ALLOWED_FIELDS = ("barcode", "product_name", "brands", "ingredients_text", "price", "stock")
TEXT_FIELDS = ("barcode", "brands", "ingredients_text")


def validate_item(data, require_name=False):
    """Check a request body and return a cleaned copy of it.

    require_name is True when creating an item (POST) and False for partial
    updates (PATCH), where the client only sends what they want to change.
    """
    if not isinstance(data, dict) or not data:
        raise ValidationError("request body must be a JSON object")

    unknown = [key for key in data if key not in ALLOWED_FIELDS]
    if unknown:
        raise ValidationError(f"unknown field(s): {', '.join(unknown)}")

    cleaned = dict(data)

    if require_name or "product_name" in cleaned:
        name = cleaned.get("product_name")
        if not isinstance(name, str) or not name.strip():
            raise ValidationError("product_name is required and must be text")
        cleaned["product_name"] = name.strip()

    if "price" in cleaned:
        price = cleaned["price"]
        # bool is a subclass of int in python so it needs its own check
        if isinstance(price, bool) or not isinstance(price, (int, float)) or price < 0:
            raise ValidationError("price must be a number that is 0 or more")

    if "stock" in cleaned:
        stock = cleaned["stock"]
        if isinstance(stock, bool) or not isinstance(stock, int) or stock < 0:
            raise ValidationError("stock must be a whole number that is 0 or more")

    for key in TEXT_FIELDS:
        if key in cleaned and not isinstance(cleaned[key], str):
            raise ValidationError(f"{key} must be text")

    return cleaned
