import pytest
from part_lister.app import app as flask_app

@pytest.fixture
def app():
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

def test_index_loads(client):
    """
    Tests that the index page loads with a 200 OK status code.
    """
    response = client.get('/')
    assert response.status_code == 200
