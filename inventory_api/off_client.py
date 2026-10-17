"""Client for the OpenFoodFacts API (https://world.openfoodfacts.org).

This module only knows how to talk to OpenFoodFacts. It returns plain dicts and
raises ExternalAPIError when something goes wrong with the network.
"""
import requests

from .errors import ExternalAPIError

BASE_URL = "https://world.openfoodfacts.org"
# OpenFoodFacts asks every app to send a custom User-Agent
HEADERS = {"User-Agent": "InventoryLab/1.0 (student project)"}
FIELDS = "code,product_name,brands,ingredients_text,quantity,categories"
TIMEOUT = 10  # seconds


def _get_json(url, params):
    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
        return response.json()
    except requests.RequestException as e:
        raise ExternalAPIError(f"could not reach OpenFoodFacts: {e}")
    except ValueError:
        raise ExternalAPIError("OpenFoodFacts sent back something that is not JSON")


def _clean(product):
    """Keep only the fields we store in our own inventory."""
    return {
        "barcode": product.get("code", ""),
        "product_name": product.get("product_name", ""),
        "brands": product.get("brands", ""),
        "ingredients_text": product.get("ingredients_text", ""),
    }


def fetch_by_barcode(barcode):
    """Return the product for a barcode, or None if OpenFoodFacts doesn't have it."""
    data = _get_json(f"{BASE_URL}/api/v2/product/{barcode}", {"fields": FIELDS})
    # status 1 means found, 0 means product not found
    if data.get("status") != 1 or "product" not in data:
        return None
    return _clean(data["product"])


def search_by_name(name, limit=5):
    """Return a list of products matching a name (empty list if none)."""
    # the v2 search has no full text search, only the older cgi endpoint does
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
