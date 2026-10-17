"""HTTP routes. Each one reads the request, calls the store or a service, and
returns JSON. Validation and error responses are handled elsewhere."""
from flask import Blueprint, current_app, jsonify, request

from .errors import ValidationError
from .validators import validate_item

bp = Blueprint("inventory", __name__)


def get_store():
    return current_app.extensions["inventory_store"]


# ---- CRUD ----

@bp.get("/inventory")
def list_items():
    return jsonify(get_store().all()), 200


@bp.get("/inventory/<int:item_id>")
def get_item(item_id):
    return jsonify(get_store().get(item_id)), 200


@bp.post("/inventory")
def add_item():
    data = validate_item(request.get_json(silent=True), require_name=True)
    return jsonify(get_store().add(data)), 201


@bp.patch("/inventory/<int:item_id>")
def update_item(item_id):
    store = get_store()
    store.get(item_id)  # 404 first, before looking at the body
    changes = validate_item(request.get_json(silent=True))
    return jsonify(store.update(item_id, changes)), 200


@bp.delete("/inventory/<int:item_id>")
def delete_item(item_id):
    get_store().delete(item_id)
    return jsonify({"message": f"item {item_id} deleted"}), 200
