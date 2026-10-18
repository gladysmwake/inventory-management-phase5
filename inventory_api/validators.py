"""Input validation and sanitization for inventory items.

Enforces strict boundary checking on incoming JSON payloads:
- Whitelist filtering: Rejects any unknown or unexpected fields (preventing mass-assignment).
- Python type nuance handling: Disallows booleans (since `bool` inherits from `int` in Python).
- Non-empty constraints: Strips whitespace and ensures positive numeric constraints.
"""
from .errors import ValidationError

# Permitted schema keys. Any key outside this set causes a 400 Bad Request error.
ALLOWED_FIELDS = ("barcode", "product_name", "brands", "ingredients_text", "price", "stock")
TEXT_FIELDS = ("barcode", "brands", "ingredients_text")


def validate_item(data, require_name=False):
    """Validate a request dictionary and return a sanitized copy.

    Args:
        data (dict): The parsed JSON payload from `request.get_json(silent=True)`.
        require_name (bool): Set to True for POST (creation) where `product_name`
            is mandatory, or False for PATCH (partial update) where fields are optional.

    Returns:
        dict: Sanitized and stripped item dictionary.

    Raises:
        ValidationError: If payload violates any data-type, range, or required constraints.
    """
    if not isinstance(data, dict) or not data:
        raise ValidationError("request body must be a JSON object")

    # Whitelist defense: reject any payload containing unrecognized keys
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

    # Price validation: must be a positive float or int.
    # Note: in Python, `issubclass(bool, int)` is True, so `isinstance(True, int)` evaluates to True.
    # An explicit check for `bool` is necessary to prevent `{"price": True}` from passing as 1.0.
    if "price" in cleaned:
        price = cleaned["price"]
        if isinstance(price, bool) or not isinstance(price, (int, float)) or price < 0:
            raise ValidationError("price must be a number that is 0 or more")

    # Stock validation: must be a non-negative whole integer (floats and booleans rejected)
    if "stock" in cleaned:
        stock = cleaned["stock"]
        if isinstance(stock, bool) or not isinstance(stock, int) or stock < 0:
            raise ValidationError("stock must be a whole number that is 0 or more")

    # String type enforcement for auxiliary metadata fields
    for key in TEXT_FIELDS:
        if key in cleaned and not isinstance(cleaned[key], str):
            raise ValidationError(f"{key} must be text")

    return cleaned
