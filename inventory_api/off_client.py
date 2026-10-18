"""Client integration for the external OpenFoodFacts API (https://world.openfoodfacts.org).

Encapsulates third-party network communication, User-Agent header compliance,
response field projection, and translation of network errors into domain exceptions.
"""
import requests

from .errors import ExternalAPIError

BASE_URL = "https://world.openfoodfacts.org"
# OpenFoodFacts API Terms of Service require apps to identify themselves via a custom User-Agent
HEADERS = {"User-Agent": "InventoryLab/1.0 (student project)"}
# Explicitly project only needed fields to keep external payload transfers lightweight
FIELDS = "code,product_name,brands,ingredients_text,quantity,categories"
# Safe network timeout preventing worker thread exhaustion if external service hangs
TIMEOUT = 10


def _get_json(url, params):
    """Execute GET request against OpenFoodFacts and parse the JSON payload.
    
    Translates raw socket, connection, timeout, and decoding failures into
    a uniform `ExternalAPIError` (which the API layer converts to HTTP 502 Bad Gateway).
    """
    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
        return response.json()
    except requests.RequestException as e:
        raise ExternalAPIError(f"could not reach OpenFoodFacts: {e}")
    except ValueError:
        raise ExternalAPIError("OpenFoodFacts sent back something that is not JSON")


def _clean(product):
    """Filter raw OpenFoodFacts payload down to our domain inventory schema."""
    return {
        "barcode": product.get("code", ""),
        "product_name": product.get("product_name", ""),
        "brands": product.get("brands", ""),
        "ingredients_text": product.get("ingredients_text", ""),
    }


def fetch_by_barcode(barcode):
    """Fetch product details for a specific barcode.
    
    OpenFoodFacts API Protocol:
    - Status code: Can be 200 even for non-existent items.
    - JSON payload status: `status: 1` indicates product exists; `status: 0` means not found.
    
    Returns:
        dict: Cleaned product dictionary if found, or None if not found.
    """
    data = _get_json(f"{BASE_URL}/api/v2/product/{barcode}", {"fields": FIELDS})
    if data.get("status") != 1 or "product" not in data:
        return None
    return _clean(data["product"])


def search_by_name(name, limit=5):
    """Execute full-text query across OpenFoodFacts product titles.
    
    Uses the `/cgi/search.pl` endpoint because OpenFoodFacts v2 lacks freeform
    full-text token matching.
    
    Returns:
        list[dict]: List of matching cleaned product dictionaries (capped at `limit`).
    """
    params = {
        "search_terms": name,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": limit,
        "fields": FIELDS,
    }
    data = _get_json(f"{BASE_URL}/cgi/search.pl", params)
    return [_clean(p) for p in data.get("products", [])]
