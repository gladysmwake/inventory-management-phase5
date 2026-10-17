"""Custom exceptions plus the handlers that turn them into JSON error responses.

Routes and services just raise these, so none of them need to build error
responses by hand.
"""
from flask import jsonify
from werkzeug.exceptions import HTTPException


class ValidationError(Exception):
    """The client sent bad input (400)."""


class ItemNotFoundError(Exception):
    """No inventory item with that id (404)."""


class ProductNotFoundError(Exception):
    """OpenFoodFacts does not know that product (404)."""


class ExternalAPIError(Exception):
    """OpenFoodFacts could not be reached or sent back junk (502)."""


def _json_error(message, status):
    return jsonify({"error": message}), status


def register_error_handlers(app):
    app.register_error_handler(ValidationError, lambda e: _json_error(str(e), 400))
    app.register_error_handler(ItemNotFoundError, lambda e: _json_error("item not found", 404))
    app.register_error_handler(ProductNotFoundError, lambda e: _json_error("product not found on OpenFoodFacts", 404))
    app.register_error_handler(ExternalAPIError, lambda e: _json_error(str(e), 502))

    # unknown urls, wrong methods etc. should also come back as JSON
    @app.errorhandler(HTTPException)
    def handle_http_error(e):
        return _json_error(e.description, e.code)
