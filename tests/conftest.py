import pytest

from inventory_api import create_app


@pytest.fixture
def app():
    # a brand new app (and store with the 3 seeded items) for every test
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    return app.test_client()
