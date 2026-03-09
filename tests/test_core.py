import json
import sqlite3


def _get_db(app_module):
    db = sqlite3.connect(app_module.app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db


def _seed_part(auth_client, barcode='CORE-001'):
    """Add a part via the admin route so it exists in the DB."""
    auth_client.post('/add_part', data={
        'barcode': barcode,
        'description': f'Part {barcode}',
        'part_number': barcode,
        'uom': 'Each',
        'supplier_name': 'Supplier',
        'stock_quantity': '10',
        'reorder_level': '2',
    }, follow_redirects=True)


# --- Index ---

def test_index_loads(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Default List' in response.data


# --- Create list ---

def test_create_list(client):
    response = client.post('/create_list', data={'list_name': 'My List'}, follow_redirects=True)
    assert response.status_code == 200
    assert b"List &#39;My List&#39; created successfully." in response.data or b'My List' in response.data


def test_create_list_empty_name(client):
    response = client.post('/create_list', data={'list_name': ''}, follow_redirects=True)
    assert response.status_code == 200
    assert b'List name cannot be empty' in response.data


def test_create_list_duplicate_name(client):
    client.post('/create_list', data={'list_name': 'Dup List'})
    response = client.post('/create_list', data={'list_name': 'Dup List'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'already exists' in response.data


# --- Switch list ---

def test_switch_list(client):
    # Create a second list
    client.post('/create_list', data={'list_name': 'Second List'})

    import part_lister.app
    db = _get_db(part_lister.app)
    list_row = db.execute("SELECT id FROM lists WHERE name = 'Second List'").fetchone()
    db.close()

    response = client.get(f'/switch_list/{list_row["id"]}', follow_redirects=True)
    assert response.status_code == 200
    assert b'Second List' in response.data


def test_switch_list_not_found(client):
    response = client.get('/switch_list/99999', follow_redirects=True)
    assert response.status_code == 200
    assert b'List not found' in response.data


# --- Add to list (JSON) ---

def test_add_to_list_json(auth_client):
    _seed_part(auth_client, 'LIST-001')

    # Set active list
    auth_client.get('/')

    response = auth_client.post('/add_to_list',
        json={'barcode': 'LIST-001', 'quantity': 2})
    assert response.status_code == 200
    data = response.get_json()
    assert data.get('barcode') == 'LIST-001' or data.get('success')


def test_add_to_list_barcode_not_found(auth_client):
    auth_client.get('/')
    response = auth_client.post('/add_to_list', json={'barcode': 'NONEXISTENT'})
    assert response.status_code == 404
    data = response.get_json()
    assert 'not found' in data['error'].lower()


def test_add_to_list_empty_barcode(auth_client):
    auth_client.get('/')
    response = auth_client.post('/add_to_list', json={'barcode': ''})
    assert response.status_code == 400


def test_add_to_list_quantity_update(auth_client):
    _seed_part(auth_client, 'QTY-001')
    auth_client.get('/')

    auth_client.post('/add_to_list', json={'barcode': 'QTY-001', 'quantity': 1})
    response = auth_client.post('/add_to_list', json={'barcode': 'QTY-001', 'quantity': 3})
    data = response.get_json()
    assert data.get('success') is True
    assert 'updated' in data.get('message', '').lower()


# --- Add to list (form) ---

def test_add_to_list_form(auth_client):
    _seed_part(auth_client, 'FORM-001')
    auth_client.get('/')

    response = auth_client.post('/add_to_list', data={
        'barcode': 'FORM-001',
        'quantity': '1',
    }, follow_redirects=True)
    assert response.status_code == 200


# --- API list items ---

def test_api_get_list_items(auth_client):
    _seed_part(auth_client, 'API-001')
    auth_client.get('/')

    auth_client.post('/add_to_list', json={'barcode': 'API-001', 'quantity': 1})

    import part_lister.app
    db = _get_db(part_lister.app)
    list_id = db.execute("SELECT id FROM lists LIMIT 1").fetchone()['id']
    db.close()

    response = auth_client.get(f'/api/lists/{list_id}/items')
    assert response.status_code == 200
    items = response.get_json()
    assert isinstance(items, list)
    assert len(items) >= 1
    assert items[0]['barcode'] == 'API-001'


# --- Edit list item ---

def test_edit_list_item(auth_client):
    _seed_part(auth_client, 'EDLI-001')
    auth_client.get('/')
    auth_client.post('/add_to_list', json={'barcode': 'EDLI-001', 'quantity': 1})

    import part_lister.app
    db = _get_db(part_lister.app)
    item = db.execute("SELECT id FROM list_items LIMIT 1").fetchone()
    db.close()

    # GET form
    response = auth_client.get(f'/edit_list_item/{item["id"]}')
    assert response.status_code == 200

    # POST update
    response = auth_client.post(f'/edit_list_item/{item["id"]}', data={'quantity': '5'}, follow_redirects=True)
    assert response.status_code == 200


# --- Delete list item ---

def test_delete_list_item(auth_client):
    _seed_part(auth_client, 'DELLI-001')
    auth_client.get('/')
    auth_client.post('/add_to_list', json={'barcode': 'DELLI-001', 'quantity': 1})

    import part_lister.app
    db = _get_db(part_lister.app)
    item = db.execute("SELECT id FROM list_items LIMIT 1").fetchone()
    db.close()

    response = auth_client.get(f'/delete_list_item/{item["id"]}', follow_redirects=True)
    assert response.status_code == 200

    db = _get_db(part_lister.app)
    row = db.execute("SELECT id FROM list_items WHERE id = ?", [item['id']]).fetchone()
    db.close()
    assert row is None


# --- Print list ---

def test_print_list(auth_client):
    _seed_part(auth_client, 'PRINT-001')
    auth_client.get('/')
    auth_client.post('/add_to_list', json={'barcode': 'PRINT-001', 'quantity': 1})

    response = auth_client.get('/print')
    assert response.status_code == 200
    assert b'PRINT-001' in response.data
