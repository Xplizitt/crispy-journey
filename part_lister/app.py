import sqlite3
import os
import csv
import io
from flask import Flask, render_template, request, redirect, url_for, session, g, flash, Response, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image

app = Flask(__name__)

# --- Configuration ---
_basedir = os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH = os.path.join(_basedir, '..', 'parts.db')
UPLOAD_FOLDER = os.path.join(_basedir, 'static', 'uploads')
THUMBNAIL_FOLDER = os.path.join(_basedir, 'static', 'thumbnails')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'zip', 'rar', '7z', 'cad'}

app.config['DATABASE'] = DATABASE_PATH
app.config['SECRET_KEY'] = 'dev'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['THUMBNAIL_FOLDER'] = THUMBNAIL_FOLDER
ADMIN_PASSWORD = 'admin'

# --- Utility Functions ---
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_thumbnail(image_path, thumbnail_path, size=(128, 128)):
    try:
        with Image.open(image_path) as img:
            img.thumbnail(size)
            img.save(thumbnail_path, "PNG")
            return True
    except IOError:
        return False

# --- Database Handling ---
def get_db():
    db_path = app.config['DATABASE']
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found at the expected path: {os.path.abspath(db_path)}")
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = sqlite3.connect(db_path)
        g.sqlite_db.row_factory = sqlite3.Row
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

# --- Routes ---
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

    query = 'SELECT p.*, GROUP_CONCAT(a.filename) as attachments FROM parts p LEFT JOIN attachments a ON p.id = a.part_id'
    conditions = []
    params = []

    if filter_description:
        conditions.append('p.description LIKE ?')
        params.append(f'%{filter_description}%')
    if filter_supplier:
        conditions.append('p.supplier_name LIKE ?')
        params.append(f'%{filter_supplier}%')
    if filter_part_number:
        conditions.append('p.part_number LIKE ?')
        params.append(f'%{filter_part_number}%')

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' GROUP BY p.id ORDER BY p.id desc'

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
    thumbnail_path = None
    try:
        cur = db.execute('''
            INSERT INTO parts (barcode, description, part_number, uom, supplier_name, notes, thumbnail)
            VALUES (?, ?, ?, ?, ?, ?, ?)''',
            [request.form['barcode'], request.form['description'], request.form['part_number'],
             request.form['uom'], request.form['supplier_name'], request.form['notes'], None])
        db.commit()
        part_id = cur.lastrowid
        flash('New part was successfully added')
    except sqlite3.IntegrityError:
        flash('Error: Barcode already exists.')
        return redirect(url_for('admin'))

    # Handle file uploads
    files = request.files.getlist('attachments')
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Create thumbnail if it's an image
            if file.mimetype.startswith('image/'):
                thumb_filename = f"thumb_{part_id}_{filename}"
                thumbnail_path = os.path.join(app.config['THUMBNAIL_FOLDER'], thumb_filename)
                if create_thumbnail(filepath, thumbnail_path):
                    db.execute('UPDATE parts SET thumbnail = ? WHERE id = ?', [thumb_filename, part_id])


            db.execute('INSERT INTO attachments (part_id, filename, filepath) VALUES (?, ?, ?)',
                       (part_id, filename, filename)) # Store relative path
            db.commit()

    return redirect(url_for('admin'))


@app.route('/edit_part/<int:part_id>', methods=['GET', 'POST'])
def edit_part(part_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    db = get_db()
    if request.method == 'POST':
        if not request.form['barcode'] or not request.form['description']:
            flash('Error: Barcode and Description are required.')
            cur = db.execute('SELECT * FROM parts WHERE id = ?', [part_id])
            part = cur.fetchone()
            return render_template('edit_part.html', part=part)

        try:
            db.execute('''
                UPDATE parts SET barcode = ?, description = ?, part_number = ?, uom = ?, supplier_name = ?, notes = ?
                WHERE id = ?''',
                [request.form['barcode'], request.form['description'], request.form['part_number'],
                 request.form['uom'], request.form['supplier_name'], request.form['notes'], part_id])
            db.commit()
            flash('Part was successfully updated')
        except sqlite3.IntegrityError:
            flash('Error: That barcode already exists.')
            cur = db.execute('SELECT * FROM parts WHERE id = ?', [part_id])
            part = cur.fetchone()
            return render_template('edit_part.html', part=part)

        # Handle file uploads
        files = request.files.getlist('attachments')
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                # Create thumbnail if it's an image and no thumbnail exists
                cur = db.execute('SELECT thumbnail FROM parts WHERE id = ?', [part_id])
                part = cur.fetchone()
                if file.mimetype.startswith('image/') and not part['thumbnail']:
                    thumb_filename = f"thumb_{part_id}_{filename}"
                    thumbnail_path = os.path.join(app.config['THUMBNAIL_FOLDER'], thumb_filename)
                    if create_thumbnail(filepath, thumbnail_path):
                        db.execute('UPDATE parts SET thumbnail = ? WHERE id = ?', [thumb_filename, part_id])

                db.execute('INSERT INTO attachments (part_id, filename, filepath) VALUES (?, ?, ?)',
                           (part_id, filename, filename))
                db.commit()

        return redirect(url_for('admin'))

    cur = db.execute('SELECT * FROM parts WHERE id = ?', [part_id])
    part = cur.fetchone()
    if part is None:
        flash('Part not found!')
        return redirect(url_for('admin'))

    cur = db.execute('SELECT * FROM attachments WHERE part_id = ?', [part_id])
    attachments = cur.fetchall()

    return render_template('edit_part.html', part=part, attachments=attachments)

@app.route('/set_thumbnail_from_filename/<int:part_id>/<filename>')
def set_thumbnail_from_filename(part_id, filename):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    db = get_db()
    # We are using filename here because the thumbnail manager query doesn't have attachment id
    cur = db.execute('SELECT id FROM attachments WHERE part_id = ? AND filename = ?', [part_id, filename])
    attachment = cur.fetchone()
    if attachment:
        return set_thumbnail(part_id, attachment['id']) # Reuse existing logic
    else:
        flash('Attachment not found.')
        return redirect(url_for('thumbnail_manager'))

@app.route('/set_thumbnail/<int:part_id>/<int:attachment_id>')
def set_thumbnail(part_id, attachment_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    db = get_db()
    cur = db.execute('SELECT filename FROM attachments WHERE id = ? AND part_id = ?', [attachment_id, part_id])
    attachment = cur.fetchone()
    if attachment:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], attachment['filename'])
        thumb_filename = f"thumb_{part_id}_{attachment['filename']}"
        thumbnail_path = os.path.join(app.config['THUMBNAIL_FOLDER'], thumb_filename)
        if create_thumbnail(filepath, thumbnail_path):
            db.execute('UPDATE parts SET thumbnail = ? WHERE id = ?', [thumb_filename, part_id])
            db.commit()
            flash('Thumbnail updated successfully.')
        else:
            flash('Error creating thumbnail.')
    else:
        flash('Attachment not found.')

    if 'thumbnail_manager' in request.referrer:
        return redirect(url_for('thumbnail_manager'))
    return redirect(url_for('edit_part', part_id=part_id))


@app.route('/clear_thumbnail/<int:part_id>')
def clear_thumbnail(part_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    db = get_db()
    db.execute('UPDATE parts SET thumbnail = NULL WHERE id = ?', [part_id])
    db.commit()
    flash('Thumbnail cleared.')

    if 'thumbnail_manager' in request.referrer:
        return redirect(url_for('thumbnail_manager'))
    return redirect(url_for('edit_part', part_id=part_id))

@app.route('/delete_attachment/<int:attachment_id>')
def delete_attachment(attachment_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    db = get_db()
    cur = db.execute('SELECT * FROM attachments WHERE id = ?', [attachment_id])
    attachment = cur.fetchone()

    if attachment:
        # Check if this is the thumbnail image
        cur = db.execute('SELECT thumbnail FROM parts WHERE id = ?', [attachment['part_id']])
        part = cur.fetchone()
        if part and part['thumbnail'] and attachment['filename'] in part['thumbnail']:
             db.execute('UPDATE parts SET thumbnail = NULL WHERE id = ?', [attachment['part_id']])

        # Delete the file from the filesystem
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], attachment['filepath']))
            # also remove thumbnail
            if part and part['thumbnail']:
                 os.remove(os.path.join(app.config['THUMBNAIL_FOLDER'], part['thumbnail']))
        except OSError as e:
            flash(f"Error deleting file: {e}")


        db.execute('DELETE FROM attachments WHERE id = ?', [attachment_id])
        db.commit()
        flash('Attachment was successfully deleted')
    else:
        flash('Attachment not found')

    return redirect(url_for('edit_part', part_id=attachment['part_id']))


@app.route('/bulk_thumbnail_action', methods=['POST'])
def bulk_thumbnail_action():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    part_ids = request.form.getlist('part_ids')
    action = request.form.get('bulk_action')

    if not part_ids:
        flash('No parts selected for bulk action.')
        return redirect(url_for('thumbnail_manager'))

    db = get_db()
    if action == 'clear':
        for part_id in part_ids:
            db.execute('UPDATE parts SET thumbnail = NULL WHERE id = ?', [part_id])
        db.commit()
        flash(f'Cleared thumbnails for {len(part_ids)} parts.')
    elif action == 'regenerate':
        regenerated_count = 0
        for part_id in part_ids:
            cur = db.execute('SELECT thumbnail FROM parts WHERE id = ?', [part_id])
            part = cur.fetchone()
            if part and part['thumbnail']:
                # The filename is in the format thumb_{part_id}_{original_filename}
                original_filename = '_'.join(part['thumbnail'].split('_')[2:])
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], original_filename)
                thumbnail_path = os.path.join(app.config['THUMBNAIL_FOLDER'], part['thumbnail'])
                if os.path.exists(filepath):
                    if create_thumbnail(filepath, thumbnail_path):
                        regenerated_count += 1
        flash(f'Regenerated {regenerated_count} thumbnails.')
    else:
        flash('Invalid bulk action.')

    return redirect(url_for('thumbnail_manager'))


@app.route('/bulk_edit', methods=['POST'])
def bulk_edit():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    part_ids = request.form.getlist('part_ids')
    action = request.form.get('bulk_action')

    if not part_ids:
        flash('No parts selected for bulk action.')
        return redirect(url_for('admin'))

    if action == 'delete':
        db = get_db()
        for part_id in part_ids:
            # This logic is duplicated from delete_part. Consider refactoring into a helper function.
            cur = db.execute('SELECT * FROM attachments WHERE part_id = ?', [part_id])
            attachments = cur.fetchall()
            for att in attachments:
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], att['filepath']))
                except OSError as e:
                    print(f"Error deleting file {att['filepath']}: {e}")

            cur = db.execute('SELECT thumbnail FROM parts WHERE id = ?', [part_id])
            part = cur.fetchone()
            if part and part['thumbnail']:
                try:
                    os.remove(os.path.join(app.config['THUMBNAIL_FOLDER'], part['thumbnail']))
                except OSError as e:
                    print(f"Error deleting thumbnail {part['thumbnail']}: {e}")

            db.execute('DELETE FROM attachments WHERE part_id = ?', [part_id])
            db.execute('DELETE FROM parts WHERE id = ?', [part_id])

        db.commit()
        flash(f'Successfully deleted {len(part_ids)} parts.')
    else:
        flash('Invalid bulk action.')

    return redirect(url_for('admin'))


@app.route('/delete_part/<int:part_id>')
def delete_part(part_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    db = get_db()
    # First, delete associated attachments from filesystem
    cur = db.execute('SELECT * FROM attachments WHERE part_id = ?', [part_id])
    attachments = cur.fetchall()
    for att in attachments:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], att['filepath']))
        except OSError as e:
            print(f"Error deleting file {att['filepath']}: {e}") # Or flash a message

    # Delete thumbnail
    cur = db.execute('SELECT thumbnail FROM parts WHERE id = ?', [part_id])
    part = cur.fetchone()
    if part and part['thumbnail']:
        try:
            os.remove(os.path.join(app.config['THUMBNAIL_FOLDER'], part['thumbnail']))
        except OSError as e:
            print(f"Error deleting thumbnail {part['thumbnail']}: {e}")


    # Delete attachment records from DB
    db.execute('DELETE FROM attachments WHERE part_id = ?', [part_id])
    # Delete the part itself
    db.execute('DELETE FROM parts WHERE id = ?', [part_id])
    db.commit()
    flash('Part and all its attachments were successfully deleted')
    return redirect(url_for('admin'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/thumbnails/<filename>')
def serve_thumbnail(filename):
    return send_from_directory(app.config['THUMBNAIL_FOLDER'], filename)


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
    writer.writerow(['Barcode', 'Description', 'Part Number', 'UOM', 'Supplier Name'])
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
        next(csv_input, None)
        db = get_db()
        imported_count = 0
        skipped_count = 0
        for row in csv_input:
            if len(row) < 5:
                continue
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
        SELECT li.id, p.barcode, p.description, li.quantity, p.uom, p.supplier_name, p.thumbnail
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
@app.route('/thumbnail_manager')
def thumbnail_manager():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    db = get_db()
    cur = db.execute('''
        SELECT p.id, p.description, p.thumbnail, GROUP_CONCAT(a.filename) as images
        FROM parts p
        JOIN attachments a ON p.id = a.part_id
        WHERE a.filename LIKE '%.jpg' OR a.filename LIKE '%.jpeg' OR a.filename LIKE '%.png' OR a.filename LIKE '%.gif'
        GROUP BY p.id
        ORDER BY p.id DESC
    ''')
    parts = cur.fetchall()
    return render_template('thumbnail_manager.html', parts=parts)

@app.route('/print')
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

# --- Main Execution ---
if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['THUMBNAIL_FOLDER'], exist_ok=True)
    app.run(debug=True, host='0.0.0.0')
