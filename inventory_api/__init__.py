from flask import Flask

from .errors import register_error_handlers
from .routes import bp
from .store import InventoryStore


def create_app(store=None):
    """Build a Flask app. Passing in a store makes testing easy."""
    app = Flask(__name__)
    app.extensions["inventory_store"] = store or InventoryStore()
    app.register_blueprint(bp)
    register_error_handlers(app)
    return app
