import io
import sqlite3


def _get_db(app_module):
    db = sqlite3.connect(app_module.app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db


def _add_part(auth_client, barcode='TEST-001', description='Test Part'):
    """Helper to add a part and return the response."""
    return auth_client.post('/add_part', data={
        'barcode': barcode,
        'description': description,
        'part_number': 'PN-001',
        'uom': 'Each',
        'supplier_name': 'Test Supplier',
        'category': 'Test',
        'location': 'Shelf A',
        'stock_quantity': '10',
        'reorder_level': '5',
        'part_type': 'Purchased',
        'notes': '',
    }, follow_redirects=True)


# --- Login / Logout ---

def test_login_page_loads(client):
    response = client.get('/login')
    assert response.status_code == 200


def test_login_success(client):
    response = client.post('/login', data={'password': 'admin'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'You were logged in' in response.data


def test_login_invalid_password(client):
    response = client.post('/login', data={'password': 'wrong'})
    assert response.status_code == 200
    assert b'Invalid password' in response.data


def test_logout(auth_client):
    response = auth_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'You were logged out' in response.data


# --- Admin page ---

def test_admin_requires_login(client):
    response = client.get('/admin')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']


def test_admin_page_loads(auth_client):
    response = auth_client.get('/admin')
    assert response.status_code == 200


# --- Parts CRUD ---

def test_add_part(auth_client):
    response = _add_part(auth_client)
    assert response.status_code == 200
    assert b'New part was successfully added' in response.data


def test_add_part_duplicate_barcode(auth_client):
    _add_part(auth_client, barcode='DUP-001')
    response = _add_part(auth_client, barcode='DUP-001')
    assert b'Error: Barcode already exists' in response.data


def test_edit_part(auth_client):
    _add_part(auth_client, barcode='EDIT-001')

    import part_lister.app
    db = _get_db(part_lister.app)
    part_id = db.execute("SELECT id FROM parts WHERE barcode = 'EDIT-001'").fetchone()['id']
    db.close()

    response = auth_client.post(f'/edit_part/{part_id}', data={
        'barcode': 'EDIT-001',
        'description': 'Updated Description',
        'part_number': 'PN-UPDATED',
        'uom': 'Box',
        'supplier_name': 'New Supplier',
        'stock_quantity': '20',
        'reorder_level': '10',
        'part_type': 'Manufactured',
        'notes': 'updated',
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Part successfully updated' in response.data


def test_edit_part_get(auth_client):
    _add_part(auth_client, barcode='EDITGET-001')

    import part_lister.app
    db = _get_db(part_lister.app)
    part_id = db.execute("SELECT id FROM parts WHERE barcode = 'EDITGET-001'").fetchone()['id']
    db.close()

    response = auth_client.get(f'/edit_part/{part_id}')
    assert response.status_code == 200
    assert b'EDITGET-001' in response.data


def test_delete_part(auth_client):
    _add_part(auth_client, barcode='DEL-001')

    import part_lister.app
    db = _get_db(part_lister.app)
    part_id = db.execute("SELECT id FROM parts WHERE barcode = 'DEL-001'").fetchone()['id']
    db.close()

    response = auth_client.get(f'/delete_part/{part_id}', follow_redirects=True)
    assert response.status_code == 200
    assert b'Part deleted' in response.data

    db = _get_db(part_lister.app)
    row = db.execute("SELECT id FROM parts WHERE barcode = 'DEL-001'").fetchone()
    db.close()
    assert row is None


def test_part_view(auth_client):
    _add_part(auth_client, barcode='VIEW-001', description='Viewable Part')

    import part_lister.app
    db = _get_db(part_lister.app)
    part_id = db.execute("SELECT id FROM parts WHERE barcode = 'VIEW-001'").fetchone()['id']
    db.close()

    response = auth_client.get(f'/part/{part_id}')
    assert response.status_code == 200
    assert b'VIEW-001' in response.data
    assert b'Viewable Part' in response.data


def test_part_view_not_found(auth_client):
    response = auth_client.get('/part/99999', follow_redirects=True)
    assert response.status_code == 200
    assert b'Part not found' in response.data


# --- Import / Export ---

def test_export_parts(auth_client):
    _add_part(auth_client, barcode='EXP-001', description='Export Part')

    response = auth_client.get('/export_parts')
    assert response.status_code == 200
    assert response.content_type == 'text/csv; charset=utf-8'
    assert b'EXP-001' in response.data
    assert b'Export Part' in response.data


def test_import_parts(auth_client):
    csv_content = 'Barcode,Description,Part Number,UOM,Supplier\nIMP-001,Imported Part,PN-IMP,Each,Supplier X\n'
    data = {
        'file': (io.BytesIO(csv_content.encode('utf-8')), 'import.csv'),
    }
    response = auth_client.post('/import_parts', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert response.status_code == 200
    assert b'Successfully imported 1 parts' in response.data


def test_import_parts_invalid_csv(auth_client):
    csv_content = 'NoBarcode,Description\nval1,val2\n'
    data = {
        'file': (io.BytesIO(csv_content.encode('utf-8')), 'bad.csv'),
    }
    response = auth_client.post('/import_parts', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid CSV format' in response.data


def test_import_parts_no_file(auth_client):
    response = auth_client.post('/import_parts', data={}, content_type='multipart/form-data', follow_redirects=True)
    assert response.status_code == 200
    assert b'No file part' in response.data


def test_import_parts_wrong_type(auth_client):
    data = {
        'file': (io.BytesIO(b'not csv'), 'bad.txt'),
    }
    response = auth_client.post('/import_parts', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid file type' in response.data


# --- Bulk edit ---

def test_bulk_delete_parts(auth_client):
    _add_part(auth_client, barcode='BULK-001')
    _add_part(auth_client, barcode='BULK-002')

    import part_lister.app
    db = _get_db(part_lister.app)
    ids = [str(r['id']) for r in db.execute("SELECT id FROM parts WHERE barcode LIKE 'BULK-%'").fetchall()]
    db.close()

    response = auth_client.post('/bulk_edit', data={
        'action': 'delete',
        'selected_parts': ids,
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Successfully deleted 2 parts' in response.data


def test_bulk_edit_no_selection(auth_client):
    response = auth_client.post('/bulk_edit', data={
        'action': 'delete',
    }, follow_redirects=True)
    assert b'No parts selected' in response.data


# --- Admin search / filter ---

def test_admin_search(auth_client):
    _add_part(auth_client, barcode='SEARCH-001', description='Findable')
    _add_part(auth_client, barcode='SEARCH-002', description='Hidden')

    response = auth_client.get('/admin?search=Findable')
    assert response.status_code == 200
    assert b'SEARCH-001' in response.data


def test_admin_category_filter(auth_client):
    _add_part(auth_client, barcode='CAT-001')

    response = auth_client.get('/admin?category=Test')
    assert response.status_code == 200
    assert b'CAT-001' in response.data


# --- Gallery ---

def test_gallery_requires_login(client):
    response = client.get('/gallery')
    assert response.status_code == 302


def test_gallery_loads(auth_client):
    response = auth_client.get('/gallery')
    assert response.status_code == 200
