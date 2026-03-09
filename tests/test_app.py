def test_index_loads(client):
    """Tests that the index page loads with a 200 OK status code."""
    response = client.get('/')
    assert response.status_code == 200
