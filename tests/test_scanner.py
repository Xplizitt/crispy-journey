def test_scanner_page_loads(client):
    """Scanner page should load without authentication."""
    response = client.get('/scanner')
    assert response.status_code == 200


def test_scanner_shows_default_list(client):
    response = client.get('/scanner')
    assert response.status_code == 200
    assert b'Default List' in response.data


def test_scanner_shows_lists(client):
    # Create a second list
    client.post('/create_list', data={'list_name': 'Scanner List'})

    response = client.get('/scanner')
    assert response.status_code == 200
    assert b'Scanner List' in response.data
