# Mile Marker: 2025-09-16 - Extracted core routes to core_bp blueprint.

from flask import Blueprint, render_template, request, session, g, flash, redirect, url_for, jsonify, send_from_directory, Response
from flask import current_app as app
import sqlite3
import os

# Note: We need get_db function from current application
def get_db():
    if not hasattr(g, 'sqlite_db'):
        db_path = app.config['DATABASE']
        g.sqlite_db = sqlite3.connect(db_path)
        g.sqlite_db.row_factory = sqlite3.Row
    return g.sqlite_db

core_bp = Blueprint('core_bp', __name__)

@core_bp.route('/')
def index():
    db = get_db()

    # Get all lists
    cur = db.execute('SELECT id, name FROM lists ORDER BY name')
    all_lists = cur.fetchall()

    # Get active list
    active_list_id = session.get('active_list_id')
    if not active_list_id:
        cur = db.execute('SELECT id, name FROM lists LIMIT 1')
        active_list = cur.fetchone()
        if active_list:
            active_list_id = active_list['id']
            session['active_list_id'] = active_list_id
    else:
        cur = db.execute('SELECT id, name FROM lists WHERE id = ?', [active_list_id])
        active_list = cur.fetchone()

    # Get items for the active list
    cur = db.execute('''
        SELECT li.id, p.id as part_id, p.barcode, p.description, p.part_number, li.quantity, p.uom, p.supplier_name, p.thumbnail
        FROM list_items li
        JOIN parts p ON li.part_id = p.id
        WHERE li.list_id = ?
        ORDER BY li.id
    ''', [active_list_id])
    list_items = cur.fetchall()

    error = session.pop('error', None)
    return render_template('index.html', list_items=list_items, all_lists=all_lists, active_list=active_list, error=error)

@core_bp.route('/add_to_list', methods=['POST'])
def add_to_list():
    if request.is_json:
        data = request.get_json()
        barcode = data.get('barcode')
        quantity = data.get('quantity', 1)
        add_as_separate = data.get('add_as_separate', False)
    else:
        barcode = request.form.get('barcode')
        quantity = request.form.get('quantity', 1)
        add_as_separate = request.form.get('add_as_separate') == 'on'

    active_list_id = session.get('active_list_id')

    if not active_list_id:
        return jsonify({'error': 'No active list selected.'}), 400
    if not barcode:
        if request.is_json:
            return jsonify({'error': 'Barcode cannot be empty.'}), 400
        else:
            flash('Barcode cannot be empty.')
            return redirect(request.referrer or url_for('core_bp.index'))

    try:
        quantity = int(quantity)
    except (ValueError, TypeError):
        quantity = 1

    db = get_db()
    cur = db.execute('SELECT * FROM parts WHERE barcode = ?', [barcode])
    part = cur.fetchone()

    if part:
        try:
            if not add_as_separate:
                # Check if the part already exists in the list
                cur = db.execute('SELECT id, quantity FROM list_items WHERE list_id = ? AND part_id = ?', [active_list_id, part['id']])
                existing_item = cur.fetchone()
                if existing_item:
                    new_quantity = existing_item['quantity'] + quantity
                    db.execute('UPDATE list_items SET quantity = ? WHERE id = ?', [new_quantity, existing_item['id']])
                    db.commit()
                    # After updating, we can just return a success message or redirect
                    if request.is_json:
                        # For AJAX requests, we might need to return the updated list or item
                        return jsonify({'success': True, 'message': 'Quantity updated.'})
                    else:
                        return redirect(request.referrer or url_for('core_bp.index'))

            # If we are adding as a separate line, or if it's a new item
            cur = db.execute('INSERT INTO list_items (list_id, part_id, quantity) VALUES (?, ?, ?)', [active_list_id, part['id'], quantity])
            db.commit()
            if request.is_json:
                new_item_id = cur.lastrowid
                cur = db.execute('''
                    SELECT li.id, p.id as part_id, p.barcode, p.description, p.part_number, li.quantity, p.uom, p.supplier_name, p.thumbnail
                    FROM list_items li
                    JOIN parts p ON li.part_id = p.id
                    WHERE li.id = ?
                ''', [new_item_id])
                new_item = cur.fetchone()
                return jsonify(dict(new_item))
            else:
                return redirect(request.referrer or url_for('core_bp.index'))
        except sqlite3.Error as e:
            if request.is_json:
                return jsonify({'error': f'Database error: {e}'}), 500
            else:
                flash(f'Database error: {e}')
                return redirect(request.referrer or url_for('core_bp.index'))
    else:
        if request.is_json:
            return jsonify({'error': 'Barcode not found.'}), 404
        else:
            session['error'] = 'Barcode not found.'
            return redirect(request.referrer or url_for('core_bp.index'))

@core_bp.route('/create_list', methods=['POST'])
def create_list():
    list_name = request.form.get('list_name')
    if not list_name:
        flash('List name cannot be empty.', 'error')
        return redirect(url_for('core_bp.index'))

    db = get_db()
    try:
        cur = db.execute('INSERT INTO lists (name) VALUES (?)', [list_name])
        db.commit()
        new_list_id = cur.lastrowid
        session['active_list_id'] = new_list_id
        flash(f"List '{list_name}' created successfully.", 'success')
    except sqlite3.IntegrityError:
        flash(f"A list with the name '{list_name}' already exists.", 'error')

    return redirect(url_for('core_bp.index'))

@core_bp.route('/switch_list/<int:list_id>')
def switch_list(list_id):
    db = get_db()
    cur = db.execute('SELECT id FROM lists WHERE id = ?', [list_id])
    if cur.fetchone():
        session['active_list_id'] = list_id
    else:
        flash('List not found.', 'error')

    # Redirect back to the referrer, defaulting to index
    referrer = request.referrer
    if referrer and 'scanner' in referrer:
        return redirect(url_for('scanner_bp.scanner'))
    return redirect(url_for('core_bp.index'))

@core_bp.route('/api/lists/<int:list_id>/items')
def api_get_list_items(list_id):
    db = get_db()
    cur = db.execute('''
        SELECT li.id, p.id as part_id, p.barcode, p.description, p.part_number, li.quantity, p.uom, p.supplier_name, p.thumbnail
        FROM list_items li
        JOIN parts p ON li.part_id = p.id
        WHERE li.list_id = ?
        ORDER BY li.id
    ''', [list_id])
    items = [dict(row) for row in cur.fetchall()]
    return jsonify(items)

@core_bp.route('/edit_list_item/<int:item_id>', methods=['GET', 'POST'])
def edit_list_item(item_id):
    origin = request.args.get('origin', 'index')
    db = get_db()

    if request.method == 'POST':
        quantity = request.form.get('quantity', 1, type=int)
        db.execute('UPDATE list_items SET quantity = ? WHERE id = ?', [quantity, item_id])
        db.commit()
        if origin == 'scanner':
            return redirect(url_for('scanner_bp.scanner'))
        return redirect(url_for('core_bp.index'))

    cur = db.execute('''
        SELECT li.id, p.barcode, p.description, li.quantity
        FROM list_items li
        JOIN parts p ON li.part_id = p.id
        WHERE li.id = ?
    ''', [item_id])
    item = cur.fetchone()

    if item is None:
        session['error'] = 'List item not found!'
        if origin == 'scanner':
            return redirect(url_for('scanner_bp.scanner'))
        return redirect(url_for('core_bp.index'))

    if origin == 'scanner':
        return render_template('edit_list_item_scanner.html', item=item)
    return render_template('edit_list_item.html', item=item)

@core_bp.route('/delete_list_item/<int:item_id>')
def delete_list_item(item_id):
    db = get_db()
    db.execute('DELETE FROM list_items WHERE id = ?', [item_id])
    db.commit()
    return redirect(url_for('core_bp.index'))

@core_bp.route('/print')
def print_list():
    db = get_db()
    cur = db.execute('''
        SELECT p.barcode, p.description, li.quantity, p.uom, p.thumbnail
        FROM list_items li
        JOIN parts p ON li.part_id = p.id
        ORDER BY li.id
    ''')
    list_items = cur.fetchall()
    return render_template('print.html', list_items=list_items)

@core_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@core_bp.route('/thumbnails/<filename>')
def serve_thumbnail(filename):
    return send_from_directory(app.config['THUMBNAIL_FOLDER'], filename)
