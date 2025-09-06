import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, g, flash

# Configuration
DATABASE = '../parts.db'
# This should be a real secret key in a production environment
ADMIN_PASSWORD = 'admin' # Simple hardcoded password
SECRET_KEY = 'dev'

app = Flask(__name__)
app.config.from_object(__name__)

def get_db():
    """Opens a new database connection if there is none yet for the current application context."""
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = sqlite3.connect(app.config['DATABASE'])
        g.sqlite_db.row_factory = sqlite3.Row
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['password'] == app.config['ADMIN_PASSWORD']:
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

@app.route('/')
def index():
    db = get_db()
    # Get items from the list, joining with parts to get details
    cur = db.execute('''
        SELECT li.id, p.barcode, p.description, li.quantity
        FROM list_items li
        JOIN parts p ON li.part_id = p.id
        ORDER BY li.id
    ''')
    list_items = cur.fetchall()

    # Check for and display any error messages
    error = session.pop('error', None)

    return render_template('index.html', list_items=list_items, error=error)

@app.route('/admin')
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    db = get_db()
    cur = db.execute('SELECT * FROM parts ORDER BY id desc')
    parts = cur.fetchall()
    return render_template('admin.html', parts=parts)

@app.route('/add_part', methods=['POST'])
def add_part():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    # Validation
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
        # Validation
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

@app.route('/print')
def print_list():
    db = get_db()
    cur = db.execute('''
        SELECT p.barcode, p.description, li.quantity
        FROM list_items li
        JOIN parts p ON li.part_id = p.id
        ORDER BY li.id
    ''')
    list_items = cur.fetchall()
    return render_template('print.html', list_items=list_items)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
