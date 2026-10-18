"""HTTP REST controllers for inventory CRUD and OpenFoodFacts lookup endpoints.
"""
from flask import Blueprint, current_app, jsonify, request

from . import off_client, services
from .errors import ProductNotFoundError, ValidationError
from .validators import validate_item

bp = Blueprint("inventory", __name__)


def get_store():
    """Retrieve the shared InventoryStore instance registered on the Flask application."""
    return current_app.extensions["inventory_store"]


# ============================================================================
# Core Inventory CRUD Endpoints
# ============================================================================

@bp.get("/inventory")
def list_items():
    """List all inventory items currently stored in the mock database."""
    return jsonify(get_store().all()), 200


@bp.get("/inventory/<int:item_id>")
def get_item(item_id):
    """Retrieve a single inventory item by ID. Returns 404 if not found."""
    return jsonify(get_store().get(item_id)), 200


@bp.post("/inventory")
def add_item():
    """Create a new inventory item.
    
    Validates payload (product_name required), appends to store, and returns HTTP 201 Created.
    """
    data = validate_item(request.get_json(silent=True), require_name=True)
    return jsonify(get_store().add(data)), 201


@bp.patch("/inventory/<int:item_id>")
def update_item(item_id):
    """Partially update an existing item's fields.
    
    Architectural Decision: Check for item existence (raising 404) BEFORE validating
    the request body. If the resource doesn't exist, we should not evaluate input data.
    """
    store = get_store()
    store.get(item_id)  # Returns 404 first if item does not exist
    changes = validate_item(request.get_json(silent=True))
    return jsonify(store.update(item_id, changes)), 200


@bp.delete("/inventory/<int:item_id>")
def delete_item(item_id):
    """Delete an item by ID. Returns confirmation message with HTTP 200."""
    get_store().delete(item_id)
    return jsonify({"message": f"item {item_id} deleted"}), 200


# ============================================================================
# Auxiliary OpenFoodFacts Helper Routes
# ============================================================================

@bp.get("/lookup/barcode/<barcode>")
def lookup_barcode(barcode):
    """Query OpenFoodFacts directly for a product by barcode string."""
    if not barcode.isdigit():
        raise ValidationError("barcode must only contain digits")
    product = off_client.fetch_by_barcode(barcode)
    if product is None:
        raise ProductNotFoundError(barcode)
    return jsonify(product), 200


@bp.get("/lookup/search")
def lookup_search():
    """Query OpenFoodFacts for products matching a name query parameter."""
    name = request.args.get("name", "").strip()
    if not name:
        raise ValidationError("name query parameter is required")
    return jsonify(off_client.search_by_name(name)), 200


@bp.post("/inventory/<int:item_id>/enrich")
def enrich_item(item_id):
    """Enrich an existing inventory item with external OpenFoodFacts metadata."""
    return jsonify(services.enrich_item(get_store(), item_id)), 200
