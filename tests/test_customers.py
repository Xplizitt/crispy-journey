import sqlite3


def test_create_customer(auth_client):
    response = auth_client.post('/customers/create', data={
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
    db.close()
    assert customer is not None


def test_view_customers(auth_client):
    auth_client.post('/customers/create', data={'name': 'Customer 1'})
    auth_client.post('/customers/create', data={'name': 'Customer 2'})

    response = auth_client.get('/customers/')
    assert response.status_code == 200
    assert b'Customer 1' in response.data
    assert b'Customer 2' in response.data


def test_create_customer_requires_name(auth_client):
    response = auth_client.post('/customers/create', data={
        'name': '',
        'email': 'test@example.com',
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Name is required.' in response.data


def test_edit_customer(auth_client):
    auth_client.post('/customers/create', data={'name': 'Original Name'})

    import part_lister.app
    db = sqlite3.connect(part_lister.app.app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    cur = db.execute('SELECT id FROM customers WHERE name = ?', ['Original Name'])
    customer_id = cur.fetchone()['id']
    db.close()

    response = auth_client.post(f'/customers/{customer_id}/edit', data={
        'name': 'Updated Name',
        'email': 'updated@example.com',
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Customer updated successfully.' in response.data
    assert b'Updated Name' in response.data


def test_delete_customer(auth_client):
    auth_client.post('/customers/create', data={'name': 'To Delete'})

    import part_lister.app
    db = sqlite3.connect(part_lister.app.app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    cur = db.execute('SELECT id FROM customers WHERE name = ?', ['To Delete'])
    customer_id = cur.fetchone()['id']
    db.close()

    response = auth_client.post(f'/customers/{customer_id}/delete', follow_redirects=True)
    assert response.status_code == 200
    assert b'Customer deleted.' in response.data


def test_view_single_customer(auth_client):
    auth_client.post('/customers/create', data={
        'name': 'View Me',
        'email': 'view@example.com',
        'phone': '555-1234',
    })

    import part_lister.app
    db = sqlite3.connect(part_lister.app.app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    cur = db.execute('SELECT id FROM customers WHERE name = ?', ['View Me'])
    customer_id = cur.fetchone()['id']
    db.close()

    response = auth_client.get(f'/customers/{customer_id}')
    assert response.status_code == 200
    assert b'View Me' in response.data
    assert b'view@example.com' in response.data


def test_search_customers(auth_client):
    auth_client.post('/customers/create', data={'name': 'Alice'})
    auth_client.post('/customers/create', data={'name': 'Bob'})

    response = auth_client.get('/customers/?search=Alice')
    assert response.status_code == 200
    assert b'Alice' in response.data
    assert b'Bob' not in response.data


def test_customer_requires_login(client):
    response = client.get('/customers/')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']
