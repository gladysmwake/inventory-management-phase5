import pytest

from inventory_api.errors import ValidationError
from inventory_api.validators import validate_item


def test_valid_new_item_passes():
    data = {"product_name": "Rice", "price": 2.5, "stock": 4}
    assert validate_item(data, require_name=True) == data


def test_name_is_stripped():
    assert validate_item({"product_name": "  Rice "}, require_name=True)["product_name"] == "Rice"


def test_name_required_for_new_item():
    with pytest.raises(ValidationError):
        validate_item({"price": 2}, require_name=True)


def test_name_not_required_for_update():
    assert validate_item({"price": 2}) == {"price": 2}


@pytest.mark.parametrize("body", [None, [], "text", {}])
def test_body_must_be_a_non_empty_object(body):
    with pytest.raises(ValidationError):
        validate_item(body)


@pytest.mark.parametrize("data", [
    {"price": -1},
    {"price": "5"},
    {"price": True},
    {"stock": -1},
    {"stock": 2.5},
    {"stock": False},
    {"brands": 5},
    {"product_name": ""},
    {"colour": "red"},
])
def test_bad_values_are_rejected(data):
    with pytest.raises(ValidationError):
        validate_item(data)
