"""Custom domain exceptions and centralized JSON error handlers.
"""
from flask import jsonify
from werkzeug.exceptions import HTTPException


class ValidationError(Exception):
    """Raised when client input fails boundary or type validation rules (maps to HTTP 400)."""


class ItemNotFoundError(Exception):
    """Raised when an inventory item ID does not exist in local store (maps to HTTP 404)."""


class ProductNotFoundError(Exception):
    """Raised when OpenFoodFacts returns no matching product for a barcode (maps to HTTP 404)."""


class ExternalAPIError(Exception):
    """Raised when upstream third-party service fails, times out, or returns invalid data (maps to HTTP 502 Bad Gateway)."""


def _json_error(message, status):
    """Construct a uniform JSON error payload."""
    return jsonify({"error": message}), status


def register_error_handlers(app):
    """Register application-level error handlers on the Flask app instance."""
    app.register_error_handler(ValidationError, lambda e: _json_error(str(e), 400))
    app.register_error_handler(ItemNotFoundError, lambda e: _json_error("item not found", 404))
    app.register_error_handler(ProductNotFoundError, lambda e: _json_error("product not found on OpenFoodFacts", 404))
    app.register_error_handler(ExternalAPIError, lambda e: _json_error(str(e), 502))

    # REST Best Practice: Ensure Werkzeug framework errors (e.g., 404 for unknown URLs,
    # 405 Method Not Allowed) return JSON payloads instead of default HTML pages.
    @app.errorhandler(HTTPException)
    def handle_http_error(e):
        return _json_error(e.description, e.code)
