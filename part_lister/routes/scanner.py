# Mile Marker: 2025-09-16 - Extracted scanner routes to scanner_bp blueprint.

from flask import Blueprint, render_template, request, session, g, flash, redirect, url_for
from flask import current_app as app
import sqlite3

# Note: We need get_db function from current application
def get_db():
    if not hasattr(g, 'sqlite_db'):
        db_path = app.config['DATABASE']
        g.sqlite_db = sqlite3.connect(db_path)
        g.sqlite_db.row_factory = sqlite3.Row
    return g.sqlite_db

scanner_bp = Blueprint('scanner_bp', __name__)

@scanner_bp.route('/scanner')
def scanner():
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
    return render_template('scanner.html', list_items=list_items, all_lists=all_lists, active_list=active_list, error=error)
