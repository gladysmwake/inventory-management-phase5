"""Wrapper around the OpenFoodFacts REST API (https://world.openfoodfacts.org).

Handles headers, timeouts, field filtering, and translates network errors
into domain exceptions the route layer can handle cleanly.
"""
import requests

from .errors import ExternalAPIError

BASE_URL = "https://world.openfoodfacts.org"
# OpenFoodFacts API Terms of Service require apps to identify themselves via a custom User-Agent
HEADERS = {"User-Agent": "InventoryLab/1.0 (student project)"}
# Explicitly project only needed fields to keep external payload transfers lightweight
FIELDS = "code,product_name,brands,ingredients_text,quantity,categories"
# safe timeout so we don't block forever if OpenFoodFacts is slow
TIMEOUT = 10


def _get_json(url, params):
    """Make a GET request to OpenFoodFacts and return parsed JSON.

    Any network or decoding failure gets re-raised as ExternalAPIError
    so the caller doesn't have to deal with raw requests exceptions.
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

    Note: OpenFoodFacts returns HTTP 200 even when nothing is found.
    We have to check `status == 1` in the JSON to know if the product exists.
    Returns a cleaned dict on success, or None if not found.
    """
    data = _get_json(f"{BASE_URL}/api/v2/product/{barcode}", {"fields": FIELDS})
    if data.get("status") != 1 or "product" not in data:
        return None
    return _clean(data["product"])


def search_by_name(name, limit=5):
    """Search OpenFoodFacts by product name.

    Uses the legacy /cgi/search.pl endpoint because the v2 API
    doesn't support free-text search yet.
    Returns a list of matching cleaned product dicts (up to `limit` results).
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
