"""Input validation helpers for inventory item payloads.

Checks types, required fields, numeric ranges, and rejects any keys
we don't recognise to stop clients sending junk we didn't ask for.
"""
from .errors import ValidationError

# Permitted schema keys. Any key outside this set causes a 400 Bad Request error.
ALLOWED_FIELDS = ("barcode", "product_name", "brands", "ingredients_text", "price", "stock")
TEXT_FIELDS = ("barcode", "brands", "ingredients_text")


def validate_item(data, require_name=False):
    """Validate a request dict and return a sanitized copy.

    Pass require_name=True for POST (product_name is mandatory),
    False for PATCH (all fields are optional).
    Raises ValidationError with a message if anything looks wrong.
    """
    if not isinstance(data, dict) or not data:
        raise ValidationError("request body must be a JSON object")

    # reject any keys we don't know about
    unknown = [key for key in data if key not in ALLOWED_FIELDS]
    if unknown:
        raise ValidationError(f"unknown field(s): {', '.join(unknown)}")

    cleaned = dict(data)

    # Validate product_name if creating or if provided in update
    if require_name or "product_name" in cleaned:
        name = cleaned.get("product_name")
        if not isinstance(name, str) or not name.strip():
            raise ValidationError("product_name is required and must be text")
        cleaned["product_name"] = name.strip()

    # price must be a real number — note: bool is a subclass of int in Python, so
    # we have to check for it explicitly or True/False would sneak through as 1/0
    if "price" in cleaned:
        price = cleaned["price"]
        if isinstance(price, bool) or not isinstance(price, (int, float)) or price < 0:
            raise ValidationError("price must be a number that is 0 or more")

    # stock must be a whole number, same bool-subclass gotcha applies
    if "stock" in cleaned:
        stock = cleaned["stock"]
        if isinstance(stock, bool) or not isinstance(stock, int) or stock < 0:
            raise ValidationError("stock must be a whole number that is 0 or more")

    # make sure the remaining text fields are actually strings
    for key in TEXT_FIELDS:
        if key in cleaned and not isinstance(cleaned[key], str):
            raise ValidationError(f"{key} must be text")

    return cleaned
