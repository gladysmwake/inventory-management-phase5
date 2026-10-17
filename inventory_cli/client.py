"""Thin wrapper around the inventory REST API. No printing and no argument
parsing here, just HTTP calls that return decoded JSON."""
import os

import requests

DEFAULT_URL = "http://127.0.0.1:5000"
TIMEOUT = 15  # seconds


class CLIError(Exception):
    """Anything that should be shown to the user as a one line error."""


class ApiClient:
    def __init__(self, base_url=None):
        self.base_url = base_url or os.environ.get("INVENTORY_API_URL", DEFAULT_URL)

    def _request(self, method, path, **kwargs):
        try:
            response = requests.request(method, self.base_url + path, timeout=TIMEOUT, **kwargs)
        except requests.ConnectionError:
            raise CLIError(f"could not connect to the API at {self.base_url}. Is app.py running?")
        except requests.RequestException as e:
            raise CLIError(f"request failed: {e}")

        try:
            body = response.json()
        except ValueError:
            raise CLIError(f"API returned an unexpected response (status {response.status_code})")

        if response.status_code >= 400:
            raise CLIError(body.get("error", f"API error {response.status_code}"))
        return body

    # inventory
    def list_items(self):
        return self._request("GET", "/inventory")

    def get_item(self, item_id):
        return self._request("GET", f"/inventory/{item_id}")

    def add_item(self, data):
        return self._request("POST", "/inventory", json=data)

    def update_item(self, item_id, changes):
        return self._request("PATCH", f"/inventory/{item_id}", json=changes)

    def delete_item(self, item_id):
        return self._request("DELETE", f"/inventory/{item_id}")

    def enrich_item(self, item_id):
        return self._request("POST", f"/inventory/{item_id}/enrich")

    # OpenFoodFacts through our API
    def lookup_barcode(self, barcode):
        return self._request("GET", f"/lookup/barcode/{barcode}")

    def search_name(self, name):
        return self._request("GET", "/lookup/search", params={"name": name})
