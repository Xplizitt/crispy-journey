from flask import Blueprint, render_template, request, session, g, flash, redirect, url_for, jsonify, current_app
import sqlite3
import os
import uuid
from werkzeug.utils import secure_filename

# Get db helper locally to avoid circular dependencies
def get_db():
    if not hasattr(g, 'sqlite_db'):
        db_path = current_app.config['DATABASE']
        g.sqlite_db = sqlite3.connect(db_path)
        g.sqlite_db.row_factory = sqlite3.Row
    return g.sqlite_db

work_orders_bp = Blueprint('work_orders_bp', __name__, url_prefix='/work_orders')

@work_orders_bp.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('admin_bp.login'))

    db = get_db()
    cur = db.execute('''SELECT w.*, c.name as customer_name FROM work_orders w LEFT JOIN customers c ON w.customer_id = c.id ORDER BY w.created_at DESC''')
    work_orders = cur.fetchall()

    cur_cust = db.execute('SELECT id, name FROM customers ORDER BY name ASC')
    customers = cur_cust.fetchall()
    return render_template('work_orders/index.html', work_orders=work_orders, customers=customers)

@work_orders_bp.route('/create', methods=['POST'])
def create():
    if not session.get('logged_in'):
        return redirect(url_for('admin_bp.login'))

    title = request.form.get('title')
    description = request.form.get('description')
    customer_id = request.form.get('customer_id')
    if not customer_id: customer_id = None

    if not title:
        flash('Title is required to create a work order.', 'error')
        return redirect(url_for('work_orders_bp.index'))

    db = get_db()
    db.execute('INSERT INTO work_orders (title, description, customer_id) VALUES (?, ?, ?)', [title, description, customer_id])
    db.commit()
    flash('Work order created successfully.', 'success')

    return redirect(url_for('work_orders_bp.index'))

@work_orders_bp.route('/<int:work_order_id>')
def view(work_order_id):
    if not session.get('logged_in'):
        return redirect(url_for('admin_bp.login'))

    db = get_db()
    cur = db.execute('''SELECT w.*, c.name as customer_name FROM work_orders w LEFT JOIN customers c ON w.customer_id = c.id WHERE w.id = ?''', [work_order_id])
    work_order = cur.fetchone()

    if not work_order:
        flash('Work order not found.', 'error')
        return redirect(url_for('work_orders_bp.index'))

    # Get Tasks
    cur = db.execute('SELECT * FROM work_order_tasks WHERE work_order_id = ? ORDER BY created_at ASC', [work_order_id])
    tasks = cur.fetchall()

    # Get parts and attachments for each task
    tasks_dict = [dict(t) for t in tasks]
    for task in tasks_dict:
        cur = db.execute('''
            SELECT tp.id, tp.quantity, p.barcode, p.description, p.part_number
            FROM task_parts tp
            JOIN parts p ON tp.part_id = p.id
            WHERE tp.task_id = ?
        ''', [task['id']])
        task['parts'] = cur.fetchall()

        cur = db.execute('SELECT * FROM work_order_attachments WHERE task_id = ?', [task['id']])
        task['attachments'] = cur.fetchall()

    # Get Logs
    cur = db.execute('SELECT * FROM work_order_logs WHERE work_order_id = ? ORDER BY created_at DESC', [work_order_id])
    logs = cur.fetchall()

    total_labor = 0.0

    # Get attachments for logs
    logs_dict = [dict(l) for l in logs]
    for log in logs_dict:
        if log.get('labor_time'):
            total_labor += log['labor_time']
        cur = db.execute('SELECT * FROM work_order_attachments WHERE log_id = ?', [log['id']])
        log['attachments'] = cur.fetchall()

    # Get general work order attachments
    cur = db.execute('SELECT * FROM work_order_attachments WHERE work_order_id = ? AND log_id IS NULL AND task_id IS NULL', [work_order_id])
    attachments = cur.fetchall()

    # Get all parts for datalist selection
    cur = db.execute('SELECT barcode, part_number, description FROM parts ORDER BY part_number ASC')
    all_parts = cur.fetchall()

    return render_template('work_orders/view.html', work_order=work_order, tasks=tasks_dict, logs=logs_dict, attachments=attachments, total_labor=total_labor, all_parts=all_parts)

@work_orders_bp.route('/<int:work_order_id>/update_status', methods=['POST'])
def update_status(work_order_id):
    if not session.get('logged_in'):
        return redirect(url_for('admin_bp.login'))

    status = request.form.get('status')
    if status not in ['Open', 'In Progress', 'Completed', 'Closed']:
        flash('Invalid status.', 'error')
        return redirect(url_for('work_orders_bp.view', work_order_id=work_order_id))

    db = get_db()
    db.execute('UPDATE work_orders SET status = ? WHERE id = ?', [status, work_order_id])
    db.commit()
    flash('Work order status updated.', 'success')

    return redirect(url_for('work_orders_bp.view', work_order_id=work_order_id))

@work_orders_bp.route('/<int:work_order_id>/add_task', methods=['POST'])
def add_task(work_order_id):
    if not session.get('logged_in'):
        return redirect(url_for('admin_bp.login'))

    description = request.form.get('description')
    customer_id = request.form.get('customer_id')
    if not customer_id: customer_id = None

    if not description:
        flash('Task description is required.', 'error')
        return redirect(url_for('work_orders_bp.view', work_order_id=work_order_id))

    db = get_db()
    db.execute('INSERT INTO work_order_tasks (work_order_id, description) VALUES (?, ?)', [work_order_id, description])
    db.commit()
    flash('Task added successfully.', 'success')

    return redirect(url_for('work_orders_bp.view', work_order_id=work_order_id))

@work_orders_bp.route('/<int:work_order_id>/update_task/<int:task_id>', methods=['POST'])
def update_task_status(work_order_id, task_id):
    if not session.get('logged_in'):
        return redirect(url_for('admin_bp.login'))

    status = request.form.get('status')
    if status not in ['TBD', 'In Progress', 'Complete']:
        flash('Invalid task status.', 'error')
        return redirect(url_for('work_orders_bp.view', work_order_id=work_order_id))

    db = get_db()
    db.execute('UPDATE work_order_tasks SET status = ? WHERE id = ? AND work_order_id = ?', [status, task_id, work_order_id])
    db.commit()
    flash('Task status updated.', 'success')

    return redirect(url_for('work_orders_bp.view', work_order_id=work_order_id))

@work_orders_bp.route('/<int:work_order_id>/task/<int:task_id>/add_part', methods=['POST'])
def add_task_part(work_order_id, task_id):
    if not session.get('logged_in'):
        return redirect(url_for('admin_bp.login'))

    barcode = request.form.get('barcode')
    quantity = request.form.get('quantity', 1, type=int)

    if not barcode:
        flash('Part barcode is required.', 'error')
        return redirect(url_for('work_orders_bp.view', work_order_id=work_order_id))

    db = get_db()
    cur = db.execute('SELECT id FROM parts WHERE barcode = ?', [barcode])
    part = cur.fetchone()

    if not part:
        flash('Part not found.', 'error')
        return redirect(url_for('work_orders_bp.view', work_order_id=work_order_id))

    db.execute('INSERT INTO task_parts (task_id, part_id, quantity) VALUES (?, ?, ?)', [task_id, part['id'], quantity])
    db.commit()
    flash('Part added to task.', 'success')

    return redirect(url_for('work_orders_bp.view', work_order_id=work_order_id))

@work_orders_bp.route('/<int:work_order_id>/add_log', methods=['POST'])
def add_log(work_order_id):
    if not session.get('logged_in'):
        return redirect(url_for('admin_bp.login'))

    labor_time = request.form.get('labor_time', 0.0, type=float)
    description = request.form.get('description')
    customer_id = request.form.get('customer_id')
    if not customer_id: customer_id = None

    if not description:
        flash('Log description is required.', 'error')
        return redirect(url_for('work_orders_bp.view', work_order_id=work_order_id))

    db = get_db()
    db.execute('INSERT INTO work_order_logs (work_order_id, labor_time, description) VALUES (?, ?, ?)', [work_order_id, labor_time, description])
    db.commit()
    flash('Log entry added.', 'success')

    return redirect(url_for('work_orders_bp.view', work_order_id=work_order_id))

def _handle_upload(file):
    if file and file.filename:
        filename = secure_filename(file.filename)
        # Add random uuid to prevent overwriting
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        return unique_filename, filepath
    return None, None

@work_orders_bp.route('/<int:work_order_id>/upload', methods=['POST'])
def upload_attachment(work_order_id):
    if not session.get('logged_in'):
        return redirect(url_for('admin_bp.login'))

    log_id = request.form.get('log_id')
    task_id = request.form.get('task_id')
    file = request.files.get('file')

    filename, filepath = _handle_upload(file)

    if not filename:
        flash('No valid file selected.', 'error')
        return redirect(url_for('work_orders_bp.view', work_order_id=work_order_id))

    db = get_db()

    # Store relative path for flexibility
    db.execute('INSERT INTO work_order_attachments (work_order_id, log_id, task_id, filename, filepath) VALUES (?, ?, ?, ?, ?)',
               [work_order_id, log_id if log_id else None, task_id if task_id else None, file.filename, filename])
    db.commit()
    flash('Attachment uploaded successfully.', 'success')

    return redirect(url_for('work_orders_bp.view', work_order_id=work_order_id))

@work_orders_bp.route('/<int:work_order_id>/delete_task/<int:task_id>', methods=['POST'])
def delete_task(work_order_id, task_id):
    if not session.get('logged_in'):
        return redirect(url_for('admin_bp.login'))

    db = get_db()
    db.execute('DELETE FROM work_order_tasks WHERE id = ? AND work_order_id = ?', [task_id, work_order_id])
    db.commit()
    flash('Task deleted.', 'success')

    return redirect(url_for('work_orders_bp.view', work_order_id=work_order_id))

@work_orders_bp.route('/<int:work_order_id>/delete_task_part/<int:task_part_id>', methods=['POST'])
def delete_task_part(work_order_id, task_part_id):
    if not session.get('logged_in'):
        return redirect(url_for('admin_bp.login'))

    db = get_db()
    db.execute('DELETE FROM task_parts WHERE id = ?', [task_part_id])
    db.commit()
    flash('Part removed from task.', 'success')

    return redirect(url_for('work_orders_bp.view', work_order_id=work_order_id))

@work_orders_bp.route('/<int:work_order_id>/delete_log/<int:log_id>', methods=['POST'])
def delete_log(work_order_id, log_id):
    if not session.get('logged_in'):
        return redirect(url_for('admin_bp.login'))

    db = get_db()
    db.execute('DELETE FROM work_order_logs WHERE id = ? AND work_order_id = ?', [log_id, work_order_id])
    db.commit()
    flash('Log entry deleted.', 'success')

    return redirect(url_for('work_orders_bp.view', work_order_id=work_order_id))
