from unittest.mock import Mock, patch

import pytest
import requests

from inventory_api import off_client
from inventory_api.errors import ExternalAPIError


def fake_response(data):
    res = Mock()
    res.json.return_value = data
    return res


def test_fetch_by_barcode_found():
    data = {"status": 1, "product": {
        "code": "3017624010701", "product_name": "Nutella", "brands": "Ferrero",
        "ingredients_text": "Sugar, palm oil", "quantity": "400 g"}}
    with patch("inventory_api.off_client.requests.get", return_value=fake_response(data)) as mock_get:
        product = off_client.fetch_by_barcode("3017624010701")

    assert product == {"barcode": "3017624010701", "product_name": "Nutella",
                       "brands": "Ferrero", "ingredients_text": "Sugar, palm oil"}
    assert mock_get.call_args.args[0].endswith("/api/v2/product/3017624010701")
    assert "User-Agent" in mock_get.call_args.kwargs["headers"]
    assert mock_get.call_args.kwargs["timeout"] == off_client.TIMEOUT


def test_fetch_by_barcode_not_found():
    data = {"status": 0, "status_verbose": "product not found"}
    with patch("inventory_api.off_client.requests.get", return_value=fake_response(data)):
        assert off_client.fetch_by_barcode("000") is None


def test_fetch_by_barcode_missing_fields_become_empty_strings():
    data = {"status": 1, "product": {"code": "1", "product_name": "Mystery"}}
    with patch("inventory_api.off_client.requests.get", return_value=fake_response(data)):
        product = off_client.fetch_by_barcode("1")
    assert product["brands"] == ""
    assert product["ingredients_text"] == ""


@pytest.mark.parametrize("error", [requests.ConnectionError("no internet"), requests.Timeout()])
def test_fetch_by_barcode_network_problems(error):
    with patch("inventory_api.off_client.requests.get", side_effect=error):
        with pytest.raises(ExternalAPIError):
            off_client.fetch_by_barcode("123")


def test_fetch_by_barcode_bad_json():
    res = Mock()
    res.json.side_effect = ValueError("no json")
    with patch("inventory_api.off_client.requests.get", return_value=res):
        with pytest.raises(ExternalAPIError):
            off_client.fetch_by_barcode("123")


def test_search_by_name_returns_cleaned_products():
    data = {"count": 2, "products": [
        {"code": "1", "product_name": "Oat Milk", "brands": "Oatly"},
        {"code": "2", "product_name": "Oat Drink", "brands": "Alpro"}]}
    with patch("inventory_api.off_client.requests.get", return_value=fake_response(data)) as mock_get:
        results = off_client.search_by_name("oat")

    assert [p["product_name"] for p in results] == ["Oat Milk", "Oat Drink"]
    assert mock_get.call_args.kwargs["params"]["search_terms"] == "oat"


def test_search_by_name_no_results():
    with patch("inventory_api.off_client.requests.get", return_value=fake_response({"products": []})):
        assert off_client.search_by_name("zzzz") == []


def test_search_by_name_network_error():
    with patch("inventory_api.off_client.requests.get", side_effect=requests.ConnectionError()):
        with pytest.raises(ExternalAPIError):
            off_client.search_by_name("milk")
