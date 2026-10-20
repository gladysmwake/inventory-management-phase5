from unittest.mock import Mock, patch

import pytest
import requests

from inventory_cli.client import ApiClient
from inventory_cli.commands import main

BASE = "http://test-server"
ITEM = {"id": 1, "barcode": "123", "product_name": "Rice", "brands": "Pishori",
        "ingredients_text": "Rice", "price": 2.5, "stock": 10}
PRODUCT = {"barcode": "123", "product_name": "Nutella", "brands": "Ferrero", "ingredients_text": "Sugar"}


def api_reply(status, body):
    res = Mock()
    res.status_code = status
    res.json.return_value = body
    return res


def run(argv, reply=None, side_effect=None):
    """Run the cli with requests.request mocked. Returns (exit code, the mock)."""
    with patch("inventory_cli.client.requests.request", return_value=reply, side_effect=side_effect) as mock_req:
        code = main(argv, client=ApiClient(BASE))
    return code, mock_req


def test_list_prints_items(capsys):
    code, mock_req = run(["list"], api_reply(200, [ITEM]))
    assert code == 0
    assert "Rice" in capsys.readouterr().out
    assert mock_req.call_args.args[:2] == ("GET", BASE + "/inventory")


def test_list_empty(capsys):
    run(["list"], api_reply(200, []))
    assert "empty" in capsys.readouterr().out


def test_view_item(capsys):
    code, mock_req = run(["view", "1"], api_reply(200, ITEM))
    assert code == 0
    assert "Pishori" in capsys.readouterr().out
    assert mock_req.call_args.args[1].endswith("/inventory/1")


def test_view_missing_item_prints_error(capsys):
    code, _ = run(["view", "99"], api_reply(404, {"error": "item not found"}))
    assert code == 1
    assert "item not found" in capsys.readouterr().err


def test_add_sends_the_right_body():
    code, mock_req = run(["add", "Rice", "--price", "2.5", "--stock", "10", "--brand", "Pishori"],
                         api_reply(201, ITEM))
    assert code == 0
    assert mock_req.call_args.args[0] == "POST"
    assert mock_req.call_args.kwargs["json"] == {
        "product_name": "Rice", "price": 2.5, "stock": 10, "brands": "Pishori"}


def test_update_sends_patch():
    code, mock_req = run(["update", "1", "--stock", "3"], api_reply(200, {**ITEM, "stock": 3}))
    assert code == 0
    assert mock_req.call_args.args[0] == "PATCH"
    assert mock_req.call_args.kwargs["json"] == {"stock": 3}


def test_update_with_nothing_to_change(capsys):
    code, mock_req = run(["update", "1"])
    assert code == 1
    mock_req.assert_not_called()
    assert "nothing to update" in capsys.readouterr().err


def test_delete(capsys):
    code, mock_req = run(["delete", "1"], api_reply(200, {"message": "item 1 deleted"}))
    assert code == 0
    assert mock_req.call_args.args[0] == "DELETE"
    assert "item 1 deleted" in capsys.readouterr().out


def test_find_by_barcode(capsys):
    code, mock_req = run(["find", "--barcode", "123"], api_reply(200, PRODUCT))
    assert code == 0
    assert mock_req.call_args.args[1].endswith("/lookup/barcode/123")
    assert "Nutella" in capsys.readouterr().out


def test_find_by_name_no_results(capsys):
    code, _ = run(["find", "--name", "zzz"], api_reply(200, []))
    assert code == 0
    assert "No products found" in capsys.readouterr().out


def test_enrich(capsys):
    code, mock_req = run(["enrich", "1"], api_reply(200, ITEM))
    assert code == 0
    assert mock_req.call_args.args[:2] == ("POST", BASE + "/inventory/1/enrich")


def test_api_not_running(capsys):
    code, _ = run(["list"], side_effect=requests.ConnectionError())
    assert code == 1
    assert "Is app.py running" in capsys.readouterr().err
