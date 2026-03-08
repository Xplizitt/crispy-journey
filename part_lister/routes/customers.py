from flask import Blueprint, render_template, request, session, g, flash, redirect, url_for
from flask import current_app as app
import sqlite3

def get_db():
    if not hasattr(g, 'sqlite_db'):
        db_path = app.config['DATABASE']
        g.sqlite_db = sqlite3.connect(db_path)
        g.sqlite_db.row_factory = sqlite3.Row
    return g.sqlite_db

customers_bp = Blueprint('customers_bp', __name__, url_prefix='/customers')

@customers_bp.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('admin_bp.login'))

    db = get_db()
    cur = db.execute('SELECT * FROM customers ORDER BY name ASC')
    customers = cur.fetchall()

    return render_template('customers/index.html', customers=customers)

@customers_bp.route('/create', methods=['GET', 'POST'])
def create():
    if not session.get('logged_in'):
        return redirect(url_for('admin_bp.login'))

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        notes = request.form.get('notes')

        if not name:
            flash('Name is required.', 'error')
            return redirect(url_for('customers_bp.create'))

        db = get_db()
        db.execute('INSERT INTO customers (name, email, phone, address, notes) VALUES (?, ?, ?, ?, ?)',
                   [name, email, phone, address, notes])
        db.commit()
        flash('Customer created successfully.', 'success')
        return redirect(url_for('customers_bp.index'))

    return render_template('customers/add.html')

@customers_bp.route('/<int:customer_id>')
def view(customer_id):
    if not session.get('logged_in'):
        return redirect(url_for('admin_bp.login'))

    db = get_db()
    cur = db.execute('SELECT * FROM customers WHERE id = ?', [customer_id])
    customer = cur.fetchone()

    if not customer:
        flash('Customer not found.', 'error')
        return redirect(url_for('customers_bp.index'))

    # Get parts assigned to this customer
    cur = db.execute('SELECT * FROM parts WHERE customer_id = ? ORDER BY part_number ASC', [customer_id])
    parts = cur.fetchall()

    # Get work orders assigned to this customer
    cur = db.execute('SELECT * FROM work_orders WHERE customer_id = ? ORDER BY created_at DESC', [customer_id])
    work_orders = cur.fetchall()

    return render_template('customers/view.html', customer=customer, parts=parts, work_orders=work_orders)

@customers_bp.route('/<int:customer_id>/edit', methods=['GET', 'POST'])
def edit(customer_id):
    if not session.get('logged_in'):
        return redirect(url_for('admin_bp.login'))

    db = get_db()
    cur = db.execute('SELECT * FROM customers WHERE id = ?', [customer_id])
    customer = cur.fetchone()

    if not customer:
        flash('Customer not found.', 'error')
        return redirect(url_for('customers_bp.index'))

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        notes = request.form.get('notes')

        if not name:
            flash('Name is required.', 'error')
            return redirect(url_for('customers_bp.edit', customer_id=customer_id))

        db.execute('UPDATE customers SET name = ?, email = ?, phone = ?, address = ?, notes = ? WHERE id = ?',
                   [name, email, phone, address, notes, customer_id])
        db.commit()
        flash('Customer updated successfully.', 'success')
        return redirect(url_for('customers_bp.view', customer_id=customer_id))

    return render_template('customers/edit.html', customer=customer)

@customers_bp.route('/<int:customer_id>/delete', methods=['POST'])
def delete(customer_id):
    if not session.get('logged_in'):
        return redirect(url_for('admin_bp.login'))

    db = get_db()

    # Check if customer is used in parts or work_orders
    cur = db.execute('SELECT COUNT(*) as count FROM parts WHERE customer_id = ?', [customer_id])
    part_count = cur.fetchone()['count']

    cur = db.execute('SELECT COUNT(*) as count FROM work_orders WHERE customer_id = ?', [customer_id])
    wo_count = cur.fetchone()['count']

    if part_count > 0 or wo_count > 0:
        flash(f'Cannot delete customer. They are assigned to {part_count} parts and {wo_count} work orders. Please reassign them first.', 'error')
        return redirect(url_for('customers_bp.view', customer_id=customer_id))

    db.execute('DELETE FROM customers WHERE id = ?', [customer_id])
    db.commit()
    flash('Customer deleted.', 'success')
    return redirect(url_for('customers_bp.index'))
