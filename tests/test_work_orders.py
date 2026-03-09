import sqlite3


def _get_db(app_module):
    db = sqlite3.connect(app_module.app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db


def _create_work_order(auth_client, title='Test WO'):
    return auth_client.post('/work_orders/create', data={
        'title': title,
        'description': 'Test description',
    }, follow_redirects=True)


def _get_wo_id(title='Test WO'):
    import part_lister.app
    db = _get_db(part_lister.app)
    row = db.execute("SELECT id FROM work_orders WHERE title = ?", [title]).fetchone()
    db.close()
    return row['id']


# --- Auth ---

def test_work_orders_requires_login(client):
    response = client.get('/work_orders/')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']


# --- Index ---

def test_work_orders_index(auth_client):
    response = auth_client.get('/work_orders/')
    assert response.status_code == 200


# --- Create ---

def test_create_work_order(auth_client):
    response = _create_work_order(auth_client)
    assert response.status_code == 200
    assert b'Work order created successfully.' in response.data


def test_create_work_order_no_title(auth_client):
    response = auth_client.post('/work_orders/create', data={
        'title': '',
    }, follow_redirects=True)
    assert b'Title is required' in response.data


# --- View ---

def test_view_work_order(auth_client):
    _create_work_order(auth_client, title='View WO')
    wo_id = _get_wo_id('View WO')

    response = auth_client.get(f'/work_orders/{wo_id}')
    assert response.status_code == 200
    assert b'View WO' in response.data


def test_view_work_order_not_found(auth_client):
    response = auth_client.get('/work_orders/99999', follow_redirects=True)
    assert response.status_code == 200
    assert b'Work order not found.' in response.data


# --- Update status ---

def test_update_work_order_status(auth_client):
    _create_work_order(auth_client, title='Status WO')
    wo_id = _get_wo_id('Status WO')

    response = auth_client.post(f'/work_orders/{wo_id}/update_status', data={
        'status': 'In Progress',
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Work order status updated.' in response.data


def test_update_work_order_invalid_status(auth_client):
    _create_work_order(auth_client, title='BadStatus WO')
    wo_id = _get_wo_id('BadStatus WO')

    response = auth_client.post(f'/work_orders/{wo_id}/update_status', data={
        'status': 'InvalidStatus',
    }, follow_redirects=True)
    assert b'Invalid status.' in response.data


# --- Tasks ---

def test_add_task(auth_client):
    _create_work_order(auth_client, title='Task WO')
    wo_id = _get_wo_id('Task WO')

    response = auth_client.post(f'/work_orders/{wo_id}/add_task', data={
        'description': 'Do something',
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Task added successfully.' in response.data


def test_add_task_no_description(auth_client):
    _create_work_order(auth_client, title='NoDescTask WO')
    wo_id = _get_wo_id('NoDescTask WO')

    response = auth_client.post(f'/work_orders/{wo_id}/add_task', data={
        'description': '',
    }, follow_redirects=True)
    assert b'Task description is required.' in response.data


def test_update_task_status(auth_client):
    _create_work_order(auth_client, title='TaskStatus WO')
    wo_id = _get_wo_id('TaskStatus WO')

    auth_client.post(f'/work_orders/{wo_id}/add_task', data={'description': 'My Task'})

    import part_lister.app
    db = _get_db(part_lister.app)
    task = db.execute("SELECT id FROM work_order_tasks WHERE work_order_id = ?", [wo_id]).fetchone()
    db.close()

    response = auth_client.post(f'/work_orders/{wo_id}/update_task/{task["id"]}', data={
        'status': 'Complete',
    }, follow_redirects=True)
    assert b'Task status updated.' in response.data


def test_delete_task(auth_client):
    _create_work_order(auth_client, title='DelTask WO')
    wo_id = _get_wo_id('DelTask WO')

    auth_client.post(f'/work_orders/{wo_id}/add_task', data={'description': 'Deleteable Task'})

    import part_lister.app
    db = _get_db(part_lister.app)
    task = db.execute("SELECT id FROM work_order_tasks WHERE work_order_id = ?", [wo_id]).fetchone()
    db.close()

    response = auth_client.post(f'/work_orders/{wo_id}/delete_task/{task["id"]}', follow_redirects=True)
    assert b'Task deleted.' in response.data


# --- Task parts ---

def test_add_task_part(auth_client):
    # Create a part first
    auth_client.post('/add_part', data={
        'barcode': 'WO-PART-001',
        'description': 'WO Part',
        'part_number': 'WOP-001',
        'uom': 'Each',
        'supplier_name': 'Sup',
        'stock_quantity': '10',
        'reorder_level': '0',
    }, follow_redirects=True)

    _create_work_order(auth_client, title='TaskPart WO')
    wo_id = _get_wo_id('TaskPart WO')

    auth_client.post(f'/work_orders/{wo_id}/add_task', data={'description': 'Needs parts'})

    import part_lister.app
    db = _get_db(part_lister.app)
    task = db.execute("SELECT id FROM work_order_tasks WHERE work_order_id = ?", [wo_id]).fetchone()
    db.close()

    response = auth_client.post(f'/work_orders/{wo_id}/task/{task["id"]}/add_part', data={
        'barcode': 'WO-PART-001',
        'quantity': '2',
    }, follow_redirects=True)
    assert b'Part added to task.' in response.data


def test_add_task_part_not_found(auth_client):
    _create_work_order(auth_client, title='BadPart WO')
    wo_id = _get_wo_id('BadPart WO')

    auth_client.post(f'/work_orders/{wo_id}/add_task', data={'description': 'Task'})

    import part_lister.app
    db = _get_db(part_lister.app)
    task = db.execute("SELECT id FROM work_order_tasks WHERE work_order_id = ?", [wo_id]).fetchone()
    db.close()

    response = auth_client.post(f'/work_orders/{wo_id}/task/{task["id"]}/add_part', data={
        'barcode': 'NONEXISTENT',
        'quantity': '1',
    }, follow_redirects=True)
    assert b'Part not found.' in response.data


# --- Logs ---

def test_add_log(auth_client):
    _create_work_order(auth_client, title='Log WO')
    wo_id = _get_wo_id('Log WO')

    response = auth_client.post(f'/work_orders/{wo_id}/add_log', data={
        'description': 'Worked on it',
        'labor_time': '1.5',
    }, follow_redirects=True)
    assert b'Log entry added.' in response.data


def test_add_log_no_description(auth_client):
    _create_work_order(auth_client, title='NoDescLog WO')
    wo_id = _get_wo_id('NoDescLog WO')

    response = auth_client.post(f'/work_orders/{wo_id}/add_log', data={
        'description': '',
        'labor_time': '0',
    }, follow_redirects=True)
    assert b'Log description is required.' in response.data


def test_delete_log(auth_client):
    _create_work_order(auth_client, title='DelLog WO')
    wo_id = _get_wo_id('DelLog WO')

    auth_client.post(f'/work_orders/{wo_id}/add_log', data={
        'description': 'Deleteable log',
        'labor_time': '0.5',
    })

    import part_lister.app
    db = _get_db(part_lister.app)
    log = db.execute("SELECT id FROM work_order_logs WHERE work_order_id = ?", [wo_id]).fetchone()
    db.close()

    response = auth_client.post(f'/work_orders/{wo_id}/delete_log/{log["id"]}', follow_redirects=True)
    assert b'Log entry deleted.' in response.data


# --- Search ---

def test_search_work_orders(auth_client):
    _create_work_order(auth_client, title='Searchable WO')
    _create_work_order(auth_client, title='Other WO')

    response = auth_client.get('/work_orders/?search=Searchable')
    assert response.status_code == 200
    assert b'Searchable WO' in response.data
