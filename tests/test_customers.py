import pytest
import sqlite3
import os
from flask import session

@pytest.fixture
def client(tmp_path):
    import part_lister.app

    db_path = tmp_path / "test.db"
    part_lister.app.app.config['DATABASE'] = str(db_path)
    part_lister.app.app.config['TESTING'] = True

    # Init DB
    with part_lister.app.app.app_context():
        import part_lister.database
        part_lister.database.DATABASE_PATH = str(db_path)
        part_lister.database.init_db()

    with part_lister.app.app.test_client() as client:
        yield client

def test_create_customer(client):
    with client.session_transaction() as sess:
        sess['logged_in'] = True

    response = client.post('/customers/create', data={
        'name': 'Test Customer',
        'email': 'test@example.com',
        'phone': '123-456-7890',
        'address': '123 Test St',
        'notes': 'Test notes'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Customer created successfully.' in response.data

    # Verify in DB
    import part_lister.app
    db = sqlite3.connect(part_lister.app.app.config['DATABASE'])
    cur = db.execute('SELECT * FROM customers WHERE name = ?', ['Test Customer'])
    customer = cur.fetchone()
    assert customer is not None

def test_view_customers(client):
    with client.session_transaction() as sess:
        sess['logged_in'] = True

    client.post('/customers/create', data={'name': 'Customer 1'})
    client.post('/customers/create', data={'name': 'Customer 2'})

    response = client.get('/customers/')
    assert response.status_code == 200
    assert b'Customer 1' in response.data
    assert b'Customer 2' in response.data
