import pytest

from inventory_api.errors import ValidationError
from inventory_api.validators import validate_item


def test_valid_item_passes():
    data = {"product_name": "Rice", "price": 2.5, "stock": 4}
    assert validate_item(data, require_name=True) == data


def test_name_is_required_for_new_items():
    with pytest.raises(ValidationError):
        validate_item({"price": 2}, require_name=True)


def test_name_not_required_for_update():
    assert validate_item({"price": 2}) == {"price": 2}


def test_negative_price_is_rejected():
    with pytest.raises(ValidationError):
        validate_item({"price": -1})


def test_negative_stock_is_rejected():
    with pytest.raises(ValidationError):
        validate_item({"stock": -5})


def test_unknown_field_is_rejected():
    with pytest.raises(ValidationError):
        validate_item({"product_name": "Rice", "colour": "white"})


def test_empty_body_is_rejected():
    with pytest.raises(ValidationError):
        validate_item({})
