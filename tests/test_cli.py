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


# ---------- commands ----------

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
    code, mock_req = run(["find", "--name", "zzz"], api_reply(200, []))
    assert code == 0
    assert mock_req.call_args.kwargs["params"] == {"name": "zzz"}
    assert "No products found" in capsys.readouterr().out


def test_enrich():
    code, mock_req = run(["enrich", "1"], api_reply(200, ITEM))
    assert code == 0
    assert mock_req.call_args.args[:2] == ("POST", BASE + "/inventory/1/enrich")


def test_import_looks_up_then_adds():
    replies = [api_reply(200, dict(PRODUCT)), api_reply(201, {**ITEM, **PRODUCT})]
    with patch("inventory_cli.client.requests.request", side_effect=replies) as mock_req:
        code = main(["import", "123", "--price", "6", "--stock", "4"], client=ApiClient(BASE))
    assert code == 0
    assert mock_req.call_count == 2
    posted = mock_req.call_args_list[1].kwargs["json"]
    assert posted["price"] == 6 and posted["stock"] == 4 and posted["product_name"] == "Nutella"


# ---------- bad input and failures ----------

@pytest.mark.parametrize("argv", [
    ["find"],
    ["add", "Rice", "--stock", "-3"],
    ["add", "Rice", "--price", "cheap"],
    ["view", "abc"],
    [],
])
def test_bad_arguments_exit_with_code_2(argv):
    # argparse exits with 2 on invalid arguments
    with pytest.raises(SystemExit) as e:
        main(argv, client=ApiClient(BASE))
    assert e.value.code == 2


def test_api_not_running(capsys):
    code, _ = run(["list"], side_effect=requests.ConnectionError())
    assert code == 1
    assert "Is app.py running" in capsys.readouterr().err


def test_other_request_failure(capsys):
    code, _ = run(["list"], side_effect=requests.Timeout("too slow"))
    assert code == 1
    assert "request failed" in capsys.readouterr().err


def test_api_returns_non_json(capsys):
    res = Mock()
    res.status_code = 500
    res.json.side_effect = ValueError()
    code, _ = run(["list"], res)
    assert code == 1
    assert "unexpected response" in capsys.readouterr().err


def test_external_api_failure_is_shown(capsys):
    code, _ = run(["find", "--barcode", "123"], api_reply(502, {"error": "could not reach OpenFoodFacts"}))
    assert code == 1
    assert "could not reach OpenFoodFacts" in capsys.readouterr().err


def test_client_reads_url_from_environment(monkeypatch):
    monkeypatch.setenv("INVENTORY_API_URL", "http://example.test:9000")
    assert ApiClient().base_url == "http://example.test:9000"
