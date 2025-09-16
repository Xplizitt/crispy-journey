import pytest
from part_lister.app import app as flask_app, get_db
from part_lister.database import init_db
import os

@pytest.fixture
def app():
    # Set up a temporary database for testing
    db_path = 'test_parts.db'
    flask_app.config.update({
        "TESTING": True,
        "DATABASE": db_path,
    })

    # Initialize the database
    with flask_app.app_context():
        # Directly call init_db, but we need to point it to the test DB
        # This is a bit of a hack because database.py has a hardcoded path
        # For a real app, this would be configured better.
        original_db_path = 'parts.db'
        if os.path.exists(original_db_path):
            os.rename(original_db_path, original_db_path + '.bak')
        if os.path.exists(db_path):
            os.remove(db_path)

        # Temporarily change the DATABASE_PATH in the database module
        import part_lister.database
        original_init_path = part_lister.database.DATABASE_PATH
        part_lister.database.DATABASE_PATH = os.path.join(os.path.dirname(__file__), '..', db_path)

        init_db()

        # Restore original path
        part_lister.database.DATABASE_PATH = original_init_path


    yield flask_app

    # Clean up the database
    if os.path.exists(db_path):
        os.remove(db_path)
    if os.path.exists(original_db_path + '.bak'):
        os.rename(original_db_path + '.bak', original_db_path)


@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

def test_create_part_and_assembly(client):
    """Tests creating both a regular part and an assembly."""
    # Login first
    client.post('/login', data={'password': 'admin'})

    # Create a regular part
    response_part = client.post('/add_part', data={
        'barcode': 'PART123',
        'description': 'A regular part',
        'part_number': 'P-123',
    }, follow_redirects=True)
    assert response_part.status_code == 200
    assert b'A regular part' in response_part.data

    # Create an assembly
    client.post('/add_part', data={
        'barcode': 'ASM123',
        'description': 'An assembly',
        'part_number': 'A-123',
        'is_assembly': '1'
    }, follow_redirects=True)

    response_admin = client.get('/admin')
    assert response_admin.status_code == 200
    assert b'An assembly' in response_admin.data
    assert b'Assembly' in response_admin.data # Check for the type badge

    # Verify in the database
    with client.application.app_context():
        db = get_db()
        part = db.execute('SELECT * FROM parts WHERE barcode = ?', ['PART123']).fetchone()
        assert part['is_assembly'] == 0
        assembly = db.execute('SELECT * FROM parts WHERE barcode = ?', ['ASM123']).fetchone()
        assert assembly['is_assembly'] == 1

def test_assembly_build_page_and_api(client):
    """Tests the assembly build page and its associated APIs."""
    client.post('/login', data={'password': 'admin'})

    # Create an assembly and two parts
    client.post('/add_part', data={'barcode': 'ASM-MAIN', 'description': 'Main Assembly', 'is_assembly': '1'})
    client.post('/add_part', data={'barcode': 'COMP1', 'description': 'Component 1'})
    client.post('/add_part', data={'barcode': 'COMP2', 'description': 'Component 2'})

    with client.application.app_context():
        db = get_db()
        assembly = db.execute('SELECT * FROM parts WHERE barcode = ?', ['ASM-MAIN']).fetchone()
        comp1 = db.execute('SELECT * FROM parts WHERE barcode = ?', ['COMP1']).fetchone()
        comp2 = db.execute('SELECT * FROM parts WHERE barcode = ?', ['COMP2']).fetchone()

    # Test that build page loads for assembly
    response = client.get(f'/build_assembly/{assembly["id"]}')
    assert response.status_code == 200
    assert b'Constituent Parts' in response.data

    # Test adding a part
    response = client.post(f'/api/assembly/{assembly["id"]}/add_part', json={'part_id': comp1["id"]})
    assert response.status_code == 200
    assert response.json['id'] == comp1['id']

    # Verify part was added
    with client.application.app_context():
        db = get_db()
        res = db.execute('SELECT * FROM assembly_parts WHERE assembly_id = ? AND part_id = ?', [assembly['id'], comp1['id']]).fetchone()
        assert res is not None

    # Test removing a part
    response = client.post(f'/api/assembly/{assembly["id"]}/remove_part', json={'part_id': comp1["id"]})
    assert response.status_code == 200
    assert response.json['success'] is True

    # Verify part was removed
    with client.application.app_context():
        db = get_db()
        res = db.execute('SELECT * FROM assembly_parts WHERE assembly_id = ? AND part_id = ?', [assembly['id'], comp1['id']]).fetchone()
        assert res is None

def test_print_view_with_assembly(client):
    """Tests the print view with collapsed and expanded assemblies."""
    client.post('/login', data={'password': 'admin'})

    # Create an assembly and a component
    client.post('/add_part', data={'barcode': 'ASM-PRINT', 'description': 'Print Assembly', 'is_assembly': '1'})
    client.post('/add_part', data={'barcode': 'COMP-PRINT', 'description': 'Print Component'})

    with client.application.app_context():
        db = get_db()
        assembly = db.execute('SELECT * FROM parts WHERE barcode = ?', ['ASM-PRINT']).fetchone()
        comp = db.execute('SELECT * FROM parts WHERE barcode = ?', ['COMP-PRINT']).fetchone()
        db.execute('INSERT INTO assembly_parts (assembly_id, part_id) VALUES (?, ?)', [assembly['id'], comp['id']])
        db.commit()

    # Visit the main page to set the session
    client.get('/')

    # Add assembly to the main list
    client.post('/add_to_list', data={'barcode': 'ASM-PRINT'})

    # Test print view with assembly collapsed
    response_collapsed = client.get('/print')
    assert response_collapsed.status_code == 200
    assert b'Print Assembly' in response_collapsed.data
    assert b'(asm)' in response_collapsed.data
    assert b'Print Component' not in response_collapsed.data

    # Test print view with assembly expanded
    response_expanded = client.get(f'/print?expanded={assembly["id"]}')
    assert response_expanded.status_code == 200
    assert b'Print Assembly' in response_expanded.data
    assert b'(asm)' not in response_expanded.data
    assert b'Print Component' in response_expanded.data

def test_scanner_view_with_assembly(client):
    """Tests that the scanner view correctly handles assemblies."""
    client.post('/login', data={'password': 'admin'})

    # Create an assembly and a component
    client.post('/add_part', data={'barcode': 'ASM-SCAN', 'description': 'Scanner Assembly', 'is_assembly': '1'})
    client.post('/add_part', data={'barcode': 'COMP-SCAN', 'description': 'Scanner Component'})

    with client.application.app_context():
        db = get_db()
        assembly = db.execute('SELECT * FROM parts WHERE barcode = ?', ['ASM-SCAN']).fetchone()
        comp = db.execute('SELECT * FROM parts WHERE barcode = ?', ['COMP-SCAN']).fetchone()
        # Add component to assembly
        db.execute('INSERT INTO assembly_parts (assembly_id, part_id) VALUES (?, ?)', [assembly['id'], comp['id']])
        db.commit()

    # Visit the main page to set the session
    client.get('/')
    # Add assembly to the main list
    client.post('/add_to_list', data={'barcode': 'ASM-SCAN'})

    # Check the scanner page
    response = client.get('/scanner')
    assert response.status_code == 200
    assert b'Scanner Assembly' in response.data
    assert b'(asm)' in response.data
    assert b'Scanner Component' in response.data
    assert b'display: none' in response.data # Check that the component row is hidden
