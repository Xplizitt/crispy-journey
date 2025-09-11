import sqlite3
import os
import csv
import io
from flask import Flask, render_template, request, redirect, url_for, session, g, flash, Response

app = Flask(__name__)

# --- Configuration ---
# Get the absolute path to the directory where this script is located
_basedir = os.path.abspath(os.path.dirname(__file__))

# Define the path for the database file in the project root directory
DATABASE_PATH = os.path.join(_basedir, '..', 'parts.db')

app.config['DATABASE'] = DATABASE_PATH
app.config['SECRET_KEY'] = 'dev' # Use a real secret key in production
app.config['ADMIN_PASSWORD'] = 'admin' # Simple hardcoded password

# --- Database Handling ---
def get_db():
    """
    Opens a new database connection if there is none yet for the current application context.
    Also, adds a check to ensure the database file exists.
    """
    db_path = app.config['DATABASE']
    if not os.path.exists(db_path):
        # This will cause a server error, but the log will clearly state the file is missing.
        raise FileNotFoundError(f"Database file not found at the expected path: {os.path.abspath(db_path)}")

    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = sqlite3.connect(db_path)
        g.sqlite_db.row_factory = sqlite3.Row
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

# --- Admin & Part Management Routes ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['password'] == ADMIN_PASSWORD:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('admin'))
        else:
            error = 'Invalid password'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('login'))

@app.route('/admin')
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    db = get_db()

    # Filtering logic
    filter_description = request.args.get('filter_description')
    filter_supplier = request.args.get('filter_supplier')
    filter_part_number = request.args.get('filter_part_number')

    query = 'SELECT * FROM parts'
    conditions = []
    params = []

    if filter_description:
        conditions.append('description LIKE ?')
        params.append(f'%{filter_description}%')
    if filter_supplier:
        conditions.append('supplier_name LIKE ?')
        params.append(f'%{filter_supplier}%')
    if filter_part_number:
        conditions.append('part_number LIKE ?')
        params.append(f'%{filter_part_number}%')

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY id desc'

    cur = db.execute(query, params)
    parts = cur.fetchall()
    return render_template('admin.html', parts=parts)

@app.route('/add_part', methods=['POST'])
def add_part():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if not request.form['barcode'] or not request.form['description']:
        flash('Error: Barcode and Description are required.')
        return redirect(url_for('admin'))

    db = get_db()
    try:
        db.execute('''
            INSERT INTO parts (barcode, description, part_number, uom, supplier_name)
            VALUES (?, ?, ?, ?, ?)''',
            [request.form['barcode'], request.form['description'], request.form['part_number'],
             request.form['uom'], request.form['supplier_name']])
        db.commit()
        flash('New part was successfully added')
    except sqlite3.IntegrityError:
        flash('Error: Barcode already exists.')

    return redirect(url_for('admin'))

@app.route('/edit_part/<int:part_id>', methods=['GET', 'POST'])
def edit_part(part_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    db = get_db()
    cur = db.execute('SELECT * FROM parts WHERE id = ?', [part_id])
    part = cur.fetchone()

    if part is None:
        flash('Part not found!')
        return redirect(url_for('admin'))

    if request.method == 'POST':
        if not request.form['barcode'] or not request.form['description']:
            flash('Error: Barcode and Description are required.')
            return render_template('edit_part.html', part=part)

        try:
            db.execute('''
                UPDATE parts SET barcode = ?, description = ?, part_number = ?, uom = ?, supplier_name = ?
                WHERE id = ?''',
                [request.form['barcode'], request.form['description'], request.form['part_number'],
                request.form['uom'], request.form['supplier_name'], part_id])
            db.commit()
            flash('Part was successfully updated')
            return redirect(url_for('admin'))
        except sqlite3.IntegrityError:
            flash('Error: That barcode already exists.')
            return render_template('edit_part.html', part=part)

    return render_template('edit_part.html', part=part)

@app.route('/delete_part/<int:part_id>')
def delete_part(part_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    db = get_db()
    db.execute('DELETE FROM parts WHERE id = ?', [part_id])
    db.commit()
    flash('Part was successfully deleted')
    return redirect(url_for('admin'))

@app.route('/export_parts')
def export_parts():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    db = get_db()

    # Reuse filtering logic from admin route
    filter_description = request.args.get('filter_description')
    filter_supplier = request.args.get('filter_supplier')
    filter_part_number = request.args.get('filter_part_number')

    query = 'SELECT barcode, description, part_number, uom, supplier_name FROM parts'
    conditions = []
    params = []

    if filter_description:
        conditions.append('description LIKE ?')
        params.append(f'%{filter_description}%')
    if filter_supplier:
        conditions.append('supplier_name LIKE ?')
        params.append(f'%{filter_supplier}%')
    if filter_part_number:
        conditions.append('part_number LIKE ?')
        params.append(f'%{filter_part_number}%')

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY id desc'

    cur = db.execute(query, params)
    parts = cur.fetchall()

    # Generate CSV
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(['Barcode', 'Description', 'Part Number', 'UOM', 'Supplier Name'])

    # Write data
    for part in parts:
        writer.writerow([part['barcode'], part['description'], part['part_number'], part['uom'], part['supplier_name']])

    output.seek(0)

    return Response(output,
                    mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=parts.csv"})

@app.route('/import_parts', methods=['POST'])
def import_parts():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('admin'))

    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('admin'))

    if file and file.filename.endswith('.csv'):
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.reader(stream)

        # Skip header row
        next(csv_input, None)

        db = get_db()
        imported_count = 0
        skipped_count = 0

        for row in csv_input:
            if len(row) < 5:
                continue # Skip malformed rows

            barcode, description, part_number, uom, supplier_name = row

            if not barcode or not description:
                skipped_count += 1
                continue

            try:
                db.execute('''
                    INSERT INTO parts (barcode, description, part_number, uom, supplier_name)
                    VALUES (?, ?, ?, ?, ?)''',
                    (barcode, description, part_number, uom, supplier_name))
                db.commit()
                imported_count += 1
            except sqlite3.IntegrityError:
                skipped_count += 1

        flash(f'Successfully imported {imported_count} parts. Skipped {skipped_count} parts (duplicates or missing data).')
    else:
        flash('Invalid file type. Please upload a CSV file.')

    return redirect(url_for('admin'))

# --- Main List-Building Routes ---
@app.route('/')
def index():
    db = get_db()
    cur = db.execute('''
        SELECT li.id, p.barcode, p.description, li.quantity, p.uom, p.supplier_name
        FROM list_items li
        JOIN parts p ON li.part_id = p.id
        ORDER BY li.id
    ''')
    list_items = cur.fetchall()

    error = session.pop('error', None)

    return render_template('index.html', list_items=list_items, error=error)

@app.route('/add_to_list', methods=['POST'])
def add_to_list():
    barcode = request.form['barcode']
    quantity = request.form.get('quantity', 1, type=int)

    if not barcode:
        session['error'] = 'Error: Barcode cannot be empty.'
        return redirect(url_for('index'))

    db = get_db()
    cur = db.execute('SELECT * FROM parts WHERE barcode = ?', [barcode])
    part = cur.fetchone()

    if part:
        db.execute('INSERT INTO list_items (part_id, quantity) VALUES (?, ?)', [part['id'], quantity])
        db.commit()
    else:
        session['error'] = 'Error: Barcode not found.'

    return redirect(url_for('index'))

@app.route('/edit_list_item/<int:item_id>', methods=['GET', 'POST'])
def edit_list_item(item_id):
    db = get_db()

    if request.method == 'POST':
        quantity = request.form.get('quantity', 1, type=int)
        db.execute('UPDATE list_items SET quantity = ? WHERE id = ?', [quantity, item_id])
        db.commit()
        return redirect(url_for('index'))

    cur = db.execute('''
        SELECT li.id, p.barcode, p.description, li.quantity
        FROM list_items li
        JOIN parts p ON li.part_id = p.id
        WHERE li.id = ?
    ''', [item_id])
    item = cur.fetchone()

    if item is None:
        session['error'] = 'List item not found!'
        return redirect(url_for('index'))

    return render_template('edit_list_item.html', item=item)

@app.route('/delete_list_item/<int:item_id>')
def delete_list_item(item_id):
    db = get_db()
    db.execute('DELETE FROM list_items WHERE id = ?', [item_id])
    db.commit()
    return redirect(url_for('index'))

# --- Print Route ---
@app.route('/print')
def print_list():
    db = get_db()
    cur = db.execute('''
        SELECT p.barcode, p.description, li.quantity, p.uom
        FROM list_items li
        JOIN parts p ON li.part_id = p.id
        ORDER BY li.id
    ''')
    list_items = cur.fetchall()
    return render_template('print.html', list_items=list_items)

# --- Main Execution ---
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
