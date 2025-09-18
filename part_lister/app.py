# ==================================================================================================
# Part Lister - Main Flask Application
# ==================================================================================================
#
# Author: AI Agent (Initial development)
# Date: 2025-09-17
#
# ## Project Overview:
# This is the core backend file for the Part Lister application. It is a monolithic Flask
# application that handles all routing, database interaction, and business logic. The
# application is designed to manage a database of parts, their associated files (attachments),
# and to build and manage picking lists.
#
# ## Key Architectural Points:
# - **Two User Interfaces:** The application serves two distinct frontends:
#   1. A modern, feature-rich interface for desktop browsers (using Bootstrap 5 and jQuery).
#   2. A lightweight, simplified "scanner" interface (`/scanner`) designed for maximum
#      compatibility with older devices, specifically handheld scanners running Windows CE 6.0
#      with Internet Explorer.
# - **Monolithic Structure:** All application logic is contained within this single file.
#   This includes user authentication, part management, file uploads, list management, and API
#   endpoints.
# - **SQLite Database:** The application uses a single SQLite database file (`parts.db`) for all
#   data persistence. Database setup and connection management are handled within this file.
# - **Templating:** Frontend pages are rendered using Flask's default Jinja2 templating engine.
# - **Session Management:** Flask's session management is used for handling admin login state.
#
# ## Core Technologies:
# - Backend: Flask (Python)
# - Database: SQLite
# - Frontend (Main): Bootstrap 5, Jinja2, custom JavaScript (`app.js`)
# - Frontend (Scanner): Basic HTML, inline CSS, and minimal inline JavaScript.
#
# ## Notes for Future Agents:
# - **Compatibility is Key:** When modifying any code related to the `/scanner` route or its
#   templates, prioritize compatibility over modern features. Avoid complex CSS and any
#   JavaScript that is not ES3-compliant.
# - **Logging:** Per `agents.md`, all changes must be logged in `agent_log.md`.
# - **Error Handling:** Pay attention to how different routes handle errors. Some return JSON
#   responses for AJAX calls, while others use `flash()` for traditional form submissions.
# - **Mile Markers:** Add a dated note to this header for any major architectural changes,
#   new features, or significant refactoring.
#
# ## Recent Changes:
# - 2025-09-17: (AI Agent) Added comprehensive header documentation and inline comments to
#   improve code clarity and maintainability.
# - 2025-09-16: (Previous Agent) Added extensive support for "Assemblies", which function like
#   parts but can contain other parts. This included new database tables, routes, API
#   endpoints, and templates.
#
import sqlite3
import os
import csv
import io
from flask import Flask, render_template, request, redirect, url_for, session, g, flash, Response, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from PIL import Image

app = Flask(__name__)

# --- Configuration ---
# Absolute path to the directory of the current script.
_basedir = os.path.abspath(os.path.dirname(__file__))
# Path to the SQLite database file, located in the parent directory of the app.
DATABASE_PATH = os.path.join(_basedir, '..', 'parts.db')
# Folder where uploaded part attachments will be stored.
UPLOAD_FOLDER = os.path.join(_basedir, 'static', 'uploads')
# Folder where generated thumbnails for images will be stored.
THUMBNAIL_FOLDER = os.path.join(_basedir, 'static', 'thumbnails')
# Set of allowed file extensions for uploads.
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'zip', 'rar', '7z', 'cad', 'dxf'}

app.config['DATABASE'] = DATABASE_PATH
app.config['SECRET_KEY'] = 'dev' # Secret key for session management. Should be changed for production.
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['THUMBNAIL_FOLDER'] = THUMBNAIL_FOLDER
ADMIN_PASSWORD = 'admin' # Simple password for the admin interface. Should be changed for production.

# --- Utility Functions ---
def allowed_file(filename):
    """Checks if a filename has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_thumbnail(image_path, thumbnail_path, size=(128, 128)):
    """Creates a thumbnail for an image file."""
    try:
        with Image.open(image_path) as img:
            img.thumbnail(size)
            img.save(thumbnail_path, "PNG")
            return True
    except IOError:
        # This can happen if the file is not an image or is corrupted.
        return False

# --- Database Handling ---
def get_db():
    """
    Opens a new database connection if there is none yet for the
    current application context. The connection is stored in Flask's `g` object,
    which is a per-request global namespace. This ensures that the database
    connection is available throughout the request lifecycle.
    """
    db_path = app.config['DATABASE']
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found at the expected path: {os.path.abspath(db_path)}")
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = sqlite3.connect(db_path)
        # Use sqlite3.Row to allow accessing columns by name.
        g.sqlite_db.row_factory = sqlite3.Row
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
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
    """
    Handles the AJAX request from the admin page to add a new part.
    Processes form data and file uploads, inserts the new part into the database,
    and returns the created part's data as JSON.
    """
    if not session.get('logged_in'):
        return jsonify({'error': 'Not logged in'}), 401

    if 'barcode' not in request.form or 'description' not in request.form:
        return jsonify({'error': 'Barcode and Description are required.'}), 400

    db = get_db()
    is_assembly = request.form.get('is_assembly', 0)
    try:
        # Insert the new part into the 'parts' table.
        cur = db.execute('''
            INSERT INTO parts (barcode, description, part_number, uom, supplier_name, notes, thumbnail, is_assembly)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            [request.form.get('barcode'), request.form.get('description'), request.form.get('part_number'),
             request.form.get('uom'), request.form.get('supplier_name'), request.form.get('notes'), None, is_assembly])
        db.commit()
        part_id = cur.lastrowid
    except sqlite3.IntegrityError:
        # This error occurs if the barcode (which is unique) already exists.
        return jsonify({'error': 'Barcode already exists.'}), 409

    # Handle file uploads associated with the new part.
    files = request.files.getlist('attachments')
    attachments_filenames = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            attachments_filenames.append(filename)

            # Insert a record for each attachment into the 'attachments' table.
            db.execute('INSERT INTO attachments (part_id, filename, filepath) VALUES (?, ?, ?)',
                       (part_id, filename, filename))
            db.commit()

    # Fetch the newly created part to return it in the JSON response.
    # This allows the frontend to dynamically update the parts table without a page reload.
    cur = db.execute('SELECT * FROM parts WHERE id = ?', [part_id])
    new_part = dict(cur.fetchone())
    new_part['attachments'] = ','.join(attachments_filenames)

    return jsonify(new_part)


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

        is_assembly = request.form.get('is_assembly', 0)
        try:
            db.execute('''
                UPDATE parts SET barcode = ?, description = ?, part_number = ?, uom = ?, supplier_name = ?, notes = ?, is_assembly = ?
                WHERE id = ?''',
                [request.form['barcode'], request.form['description'], request.form['part_number'],
                 request.form['uom'], request.form['supplier_name'], request.form['notes'], is_assembly, part_id])
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


@app.route('/build_assembly/<int:part_id>', methods=['GET'])
def build_assembly(part_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    db = get_db()

    # Fetch the main assembly part details
    cur = db.execute('SELECT * FROM parts WHERE id = ? AND is_assembly = 1', [part_id])
    part = cur.fetchone()
    if part is None:
        flash('Assembly not found!')
        return redirect(url_for('admin'))

    # Fetch constituent parts
    cur = db.execute('''
        SELECT p.* FROM parts p
        JOIN assembly_parts ap ON p.id = ap.part_id
        WHERE ap.assembly_id = ?
    ''', [part_id])
    constituent_parts = cur.fetchall()

    # Fetch attachments
    cur = db.execute('SELECT * FROM attachments WHERE part_id = ?', [part_id])
    attachments = cur.fetchall()

    return render_template('build_assembly.html', part=part, attachments=attachments, constituent_parts=constituent_parts)


@app.route('/part/<int:part_id>')
def part_view(part_id):
    origin = request.args.get('origin', 'admin')
    db = get_db()
    cur = db.execute('SELECT * FROM parts WHERE id = ?', [part_id])
    part = cur.fetchone()
    if part is None:
        flash('Part not found!')
        return redirect(url_for('admin'))

    cur = db.execute('SELECT * FROM attachments WHERE part_id = ?', [part_id])
    attachments = cur.fetchall()

    image_attachments = []
    file_attachments = []
    image_extensions = ['.png', '.jpg', '.jpeg', '.gif']

    for attachment in attachments:
        if any(attachment['filename'].lower().endswith(ext) for ext in image_extensions):
            image_attachments.append(attachment)
        else:
            file_attachments.append(attachment)

    return render_template('part_view.html', part=part, image_attachments=image_attachments, file_attachments=file_attachments, origin=origin)

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
    return redirect(url_for('edit_part', part_id=part_id))


@app.route('/clear_thumbnail/<int:part_id>')
def clear_thumbnail(part_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    db = get_db()
    db.execute('UPDATE parts SET thumbnail = NULL WHERE id = ?', [part_id])
    db.commit()
    flash('Thumbnail cleared.')
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


@app.route('/apply_thumbnail/<filename>')
def apply_thumbnail(filename):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    part_ids_str = request.args.get('part_ids')
    if not part_ids_str:
        flash('No parts selected.')
        return redirect(url_for('admin'))

    part_ids = part_ids_str.split(',')
    db = get_db()

    # Check if the image exists as an attachment
    cur = db.execute('SELECT id FROM attachments WHERE filename = ?', [filename])
    attachment = cur.fetchone()
    if not attachment:
        flash('Selected image not found.')
        return redirect(url_for('admin'))

    # Create the thumbnail file
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    updated_count = 0
    for part_id in part_ids:
        thumb_filename = f"thumb_{part_id}_{filename}"
        thumbnail_path = os.path.join(app.config['THUMBNAIL_FOLDER'], thumb_filename)
        if create_thumbnail(filepath, thumbnail_path):
            db.execute('UPDATE parts SET thumbnail = ? WHERE id = ?', [thumb_filename, part_id])
            updated_count += 1

    db.commit()
    flash(f'Successfully set thumbnail for {updated_count} part(s).')

    # If we only updated one part, redirect back to its edit page.
    if len(part_ids) == 1:
        return redirect(url_for('edit_part', part_id=part_ids[0]))
    else:
        return redirect(url_for('admin'))


@app.route('/select_thumbnail')
def select_thumbnail():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    part_ids = request.args.get('part_ids')
    if not part_ids:
        flash('No parts selected.')
        return redirect(url_for('admin'))

    db = get_db()
    cur = db.execute('''
        SELECT id, filename FROM attachments
        WHERE (filename LIKE '%.jpg' OR filename LIKE '%.jpeg' OR filename LIKE '%.png' OR filename LIKE '%.gif')
        AND filename NOT LIKE '%.dxf'
        ORDER BY id DESC
    ''')
    images = cur.fetchall()
    return render_template('select_thumbnail.html', images=images, part_ids=part_ids)


def _delete_part_thumbnail_file(part_id):
    """Helper function to delete the thumbnail file for a given part."""
    db = get_db()
    cur = db.execute('SELECT thumbnail FROM parts WHERE id = ?', [part_id])
    part = cur.fetchone()
    if part and part['thumbnail']:
        try:
            os.remove(os.path.join(app.config['THUMBNAIL_FOLDER'], part['thumbnail']))
        except OSError as e:
            # Log error but don't flash to user, as it's a background cleanup task.
            print(f"Error deleting thumbnail file {part['thumbnail']}: {e}")

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
            _delete_part_thumbnail_file(part_id)
            # The ON DELETE SET NULL constraint handles detaching attachments.
            db.execute('DELETE FROM parts WHERE id = ?', [part_id])

        db.commit()
        flash(f'Successfully deleted {len(part_ids)} parts.')
    elif action == 'set_thumbnail':
        return redirect(url_for('select_thumbnail', part_ids=','.join(part_ids)))
    else:
        flash('Invalid bulk action.')

    return redirect(url_for('admin'))


@app.route('/delete_part/<int:part_id>')
def delete_part(part_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    db = get_db()
    _delete_part_thumbnail_file(part_id)

    # The attachments themselves are NOT deleted.
    # The ON DELETE SET NULL constraint in the DB will set their part_id to NULL.

    # Delete the part itself
    db.execute('DELETE FROM parts WHERE id = ?', [part_id])
    db.commit()
    flash('Part was successfully deleted. Its attachments are now in the global gallery.')
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
            barcode, description, part_number, uom, supplier_name = row[:5] # Take the first 5 columns
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

    # Ensure there's an active list in the session
    if 'active_list_id' not in session:
        # Find the first list (which is the default) and set it as active
        cur = db.execute('SELECT id FROM lists ORDER BY id LIMIT 1')
        first_list = cur.fetchone()
        if first_list:
            session['active_list_id'] = first_list['id']
        else:
            # Handle case where database might be empty
            return "Error: No lists found in the database. Please initialize it.", 500

    active_list_id = session['active_list_id']

    # Get all lists for the dropdown switcher
    cur = db.execute('SELECT * FROM lists ORDER BY name')
    all_lists = cur.fetchall()

    # Get the details of the active list
    cur = db.execute('SELECT * FROM lists WHERE id = ?', [active_list_id])
    active_list = cur.fetchone()

    # Get items for the active list
    cur = db.execute('''
        SELECT li.id, p.id as part_id, p.barcode, p.description, p.part_number, li.quantity, p.uom, p.supplier_name, p.thumbnail, p.is_assembly
        FROM list_items li
        JOIN parts p ON li.part_id = p.id
        WHERE li.list_id = ?
        ORDER BY li.id
    ''', [active_list_id])

    list_items_rows = cur.fetchall()
    list_items = []
    for item in list_items_rows:
        item_dict = dict(item)
        if item_dict['is_assembly']:
            cur = db.execute('''
                SELECT p.part_number, p.description, p.uom
                FROM assembly_parts ap
                JOIN parts p ON ap.part_id = p.id
                WHERE ap.assembly_id = ?
            ''', [item_dict['part_id']])
            item_dict['components'] = [dict(row) for row in cur.fetchall()]
        else:
            item_dict['components'] = []
        list_items.append(item_dict)


    error = session.pop('error', None)
    return render_template('index.html', list_items=list_items, all_lists=all_lists, active_list=active_list, error=error)

@app.route('/scanner')
def scanner():
    """
    Renders the simplified scanner interface. This route is intentionally separate from
    the main `index` route to serve a different HTML template (`scanner.html`) that is
    optimized for older, resource-constrained devices. The backend logic for fetching
    list data is nearly identical to the `index` route.
    """
    db = get_db()

    # Ensure there's an active list in the session. If not, default to the first list.
    if 'active_list_id' not in session:
        cur = db.execute('SELECT id FROM lists ORDER BY id LIMIT 1')
        first_list = cur.fetchone()
        if first_list:
            session['active_list_id'] = first_list['id']
        else:
            return "Error: No lists found in the database. Please initialize it.", 500

    active_list_id = session['active_list_id']

    # Get all lists for the dropdown list switcher.
    cur = db.execute('SELECT * FROM lists ORDER BY name')
    all_lists = cur.fetchall()

    # Get the details of the currently active list.
    cur = db.execute('SELECT * FROM lists WHERE id = ?', [active_list_id])
    active_list = cur.fetchone()

    # Get all items for the active list, joining with the parts table.
    cur = db.execute('''
        SELECT li.id, p.id as part_id, p.barcode, p.description, p.part_number, li.quantity, p.uom, p.supplier_name, p.thumbnail, p.is_assembly
        FROM list_items li
        JOIN parts p ON li.part_id = p.id
        WHERE li.list_id = ?
        ORDER BY li.id
    ''', [active_list_id])

    list_items_rows = cur.fetchall()
    list_items = []
    # For each item, if it's an assembly, fetch its constituent components.
    for item in list_items_rows:
        item_dict = dict(item)
        if item_dict['is_assembly']:
            cur = db.execute('''
                SELECT p.part_number, p.description, p.uom
                FROM assembly_parts ap
                JOIN parts p ON ap.part_id = p.id
                WHERE ap.assembly_id = ?
            ''', [item_dict['part_id']])
            item_dict['components'] = [dict(row) for row in cur.fetchall()]
        else:
            item_dict['components'] = []
        list_items.append(item_dict)

    # Get scan status from URL parameters to pass to the template for feedback UI.
    scan_status = {
        "status": request.args.get('scan_status'),
        "message": request.args.get('message'),
        "barcode": request.args.get('barcode'),
        "qty": request.args.get('qty')
    }

    return render_template('scanner.html', list_items=list_items, all_lists=all_lists, active_list=active_list, scan_status=scan_status)

@app.route('/add_to_list', methods=['POST'])
def add_to_list():
    """
    Handles adding an item to the active list. This route is designed to handle
    requests from both the main interface (as JSON) and the scanner interface
    (as a standard form submission).
    """
    is_scanner_request = 'scanner' in (request.referrer or '')

    # Check if the request is an AJAX call with a JSON payload.
    if request.is_json:
        data = request.get_json()
        barcode = data.get('barcode')
        quantity = data.get('quantity', 1)
        add_as_separate = data.get('add_as_separate', False)
    # Otherwise, handle it as a traditional form submission.
    else:
        barcode = request.form.get('barcode')
        quantity = request.form.get('quantity', 1)
        add_as_separate = request.form.get('add_as_separate') == 'on'

    active_list_id = session.get('active_list_id')

    if not active_list_id:
        # This error should ideally only be seen by API clients.
        return jsonify({'error': 'No active list selected.'}), 400
    if not barcode:
        if is_scanner_request:
            return redirect(url_for('scanner', scan_status='error', message='Barcode cannot be empty.'))
        elif request.is_json:
            return jsonify({'error': 'Barcode cannot be empty.'}), 400
        else:
            # For form submissions from main UI, flash a message and redirect.
            flash('Barcode cannot be empty.')
            return redirect(request.referrer or url_for('index'))

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
                    if is_scanner_request:
                         return redirect(url_for('scanner', scan_status='success', barcode=part['barcode'], qty=quantity))
                    elif request.is_json:
                        return jsonify({'success': True, 'message': 'Quantity updated.'})
                    else:
                        return redirect(request.referrer or url_for('index'))

            # If we are adding as a separate line, or if it's a new item
            cur = db.execute('INSERT INTO list_items (list_id, part_id, quantity) VALUES (?, ?, ?)', [active_list_id, part['id'], quantity])
            db.commit()
            if is_scanner_request:
                 return redirect(url_for('scanner', scan_status='success', barcode=part['barcode'], qty=quantity))
            elif request.is_json:
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
                return redirect(request.referrer or url_for('index'))
        except sqlite3.Error as e:
            if is_scanner_request:
                return redirect(url_for('scanner', scan_status='error', message=f'Database error: {e}'))
            elif request.is_json:
                return jsonify({'error': f'Database error: {e}'}), 500
            else:
                flash(f'Database error: {e}')
                return redirect(request.referrer or url_for('index'))
    else:
        if is_scanner_request:
            return redirect(url_for('scanner', scan_status='error', message='Barcode not found.'))
        elif request.is_json:
            return jsonify({'error': 'Barcode not found.'}), 404
        else:
            session['error'] = 'Barcode not found.'
            return redirect(request.referrer or url_for('index'))

@app.route('/create_list', methods=['POST'])
def create_list():
    list_name = request.form.get('list_name')
    if not list_name:
        flash('List name cannot be empty.', 'error')
        return redirect(url_for('index'))

    db = get_db()
    try:
        cur = db.execute('INSERT INTO lists (name) VALUES (?)', [list_name])
        db.commit()
        new_list_id = cur.lastrowid
        session['active_list_id'] = new_list_id
        flash(f"List '{list_name}' created successfully.", 'success')
    except sqlite3.IntegrityError:
        flash(f"A list with the name '{list_name}' already exists.", 'error')

    return redirect(url_for('index'))

@app.route('/switch_list/<int:list_id>')
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
        return redirect(url_for('scanner'))
    return redirect(url_for('index'))

@app.route('/api/lists/<int:list_id>/items')
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


@app.route('/api/parts/search')
def api_parts_search():
    if not session.get('logged_in'):
        return jsonify({'error': 'Not logged in'}), 401

    query = request.args.get('q', '')
    assembly_id = request.args.get('assembly_id', type=int)

    if not query:
        return jsonify([])

    db = get_db()

    sql_query = '''
        SELECT id, description, part_number FROM parts
        WHERE (description LIKE ? OR part_number LIKE ?)
    '''
    params = [f'%{query}%', f'%{query}%']

    if assembly_id:
        sql_query += ' AND id != ?'
        params.append(assembly_id)

    # Exclude parts that are already assemblies
    sql_query += ' AND is_assembly = 0'

    sql_query += ' LIMIT 10'

    cur = db.execute(sql_query, params)
    parts = [dict(row) for row in cur.fetchall()]
    return jsonify(parts)


@app.route('/api/assembly/<int:assembly_id>/add_part', methods=['POST'])
def api_add_part_to_assembly(assembly_id):
    if not session.get('logged_in'):
        return jsonify({'error': 'Not logged in'}), 401

    data = request.get_json()
    part_id = data.get('part_id')

    if not part_id:
        return jsonify({'error': 'Part ID is required.'}), 400

    db = get_db()
    try:
        db.execute('INSERT INTO assembly_parts (assembly_id, part_id) VALUES (?, ?)', [assembly_id, part_id])
        db.commit()
    except sqlite3.IntegrityError:
        # This can happen if the part is already in the assembly, which is fine.
        # It can also happen if the part_id or assembly_id doesn't exist, which is a problem.
        # For now, we'll just assume the former.
        pass

    cur = db.execute('SELECT * FROM parts WHERE id = ?', [part_id])
    part = dict(cur.fetchone())
    return jsonify(part)


@app.route('/api/assembly/<int:assembly_id>/remove_part', methods=['POST'])
def api_remove_part_from_assembly(assembly_id):
    if not session.get('logged_in'):
        return jsonify({'error': 'Not logged in'}), 401

    data = request.get_json()
    part_id = data.get('part_id')

    if not part_id:
        return jsonify({'error': 'Part ID is required.'}), 400

    db = get_db()
    db.execute('DELETE FROM assembly_parts WHERE assembly_id = ? AND part_id = ?', [assembly_id, part_id])
    db.commit()

    return jsonify({'success': True})


@app.route('/edit_list_item/<int:item_id>', methods=['GET', 'POST'])
def edit_list_item(item_id):
    origin = request.args.get('origin', 'index')
    db = get_db()

    if request.method == 'POST':
        quantity = request.form.get('quantity', 1, type=int)
        db.execute('UPDATE list_items SET quantity = ? WHERE id = ?', [quantity, item_id])
        db.commit()
        if origin == 'scanner':
            return redirect(url_for('scanner'))
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
        if origin == 'scanner':
            return redirect(url_for('scanner'))
        return redirect(url_for('index'))

    if origin == 'scanner':
        return render_template('edit_list_item_scanner.html', item=item)
    return render_template('edit_list_item.html', item=item)

@app.route('/delete_list_item/<int:item_id>')
def delete_list_item(item_id):
    db = get_db()
    db.execute('DELETE FROM list_items WHERE id = ?', [item_id])
    db.commit()
    return redirect(url_for('index'))

# --- Print Route ---
@app.route('/delete_image/<int:image_id>')
def delete_image(image_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    db = get_db()
    cur = db.execute('SELECT filename FROM attachments WHERE id = ?', [image_id])
    image = cur.fetchone()
    if not image:
        flash('Image not found.')
        return redirect(url_for('gallery'))

    # Check if this image is used as a thumbnail
    thumb_filename_pattern = f"%thumb_%_{image['filename']}"
    cur = db.execute('SELECT COUNT(*) as count FROM parts WHERE thumbnail LIKE ?', [thumb_filename_pattern])
    usage = cur.fetchone()
    if usage['count'] > 0:
        flash(f"Cannot delete image. It is currently used as a thumbnail for {usage['count']} part(s). Please assign a different thumbnail to those parts first.")
        return redirect(url_for('gallery'))

    # Delete file from uploads folder
    try:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], image['filename']))
    except OSError as e:
        flash(f"Error deleting file from filesystem: {e}")

    # Delete record from database
    db.execute('DELETE FROM attachments WHERE id = ?', [image_id])
    db.commit()
    flash(f"Image '{image['filename']}' deleted successfully.")
    return redirect(url_for('gallery'))


@app.route('/gallery', methods=['GET', 'POST'])
def gallery():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    db = get_db()

    if request.method == 'POST':
        if 'files' not in request.files:
            flash('No file part')
            return redirect(request.url)
        files = request.files.getlist('files')
        for file in files:
            if file.filename == '':
                continue
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                db.execute('INSERT INTO attachments (part_id, filename, filepath) VALUES (?, ?, ?)',
                           (None, filename, filename))
        db.commit()
        flash(f'Successfully uploaded {len(files)} files.')
        return redirect(url_for('gallery'))

    cur = db.execute('''
        SELECT id, filename FROM attachments
        WHERE filename LIKE '%.jpg' OR filename LIKE '%.jpeg' OR filename LIKE '%.png' OR filename LIKE '%.gif'
        ORDER BY id DESC
    ''')
    images = cur.fetchall()
    return render_template('gallery.html', images=images)


@app.route('/print')
def print_list():
    expanded_ids_str = request.args.get('expanded', '')
    expanded_ids = []
    if expanded_ids_str:
        try:
            expanded_ids = [int(id_str) for id_str in expanded_ids_str.split(',')]
        except ValueError:
            expanded_ids = [] # Ignore if the param is malformed

    db = get_db()
    active_list_id = session.get('active_list_id')
    if not active_list_id:
        return "No active list found.", 404

    cur = db.execute('''
        SELECT li.id, p.id as part_id, p.barcode, p.description, p.part_number, li.quantity, p.uom, p.thumbnail, p.is_assembly
        FROM list_items li
        JOIN parts p ON li.part_id = p.id
        WHERE li.list_id = ?
        ORDER BY li.id
    ''', [active_list_id])

    list_items_rows = cur.fetchall()
    list_items = []
    for item in list_items_rows:
        item_dict = dict(item)
        if item_dict['is_assembly']:
            cur = db.execute('''
                SELECT p.part_number, p.description, p.uom
                FROM assembly_parts ap
                JOIN parts p ON ap.part_id = p.id
                WHERE ap.assembly_id = ?
            ''', [item_dict['part_id']])
            item_dict['components'] = [dict(row) for row in cur.fetchall()]
        else:
            item_dict['components'] = []
        list_items.append(item_dict)

    return render_template('print.html', list_items=list_items, expanded_ids=expanded_ids)

# --- Main Execution ---
if __name__ == '__main__':
    # This block runs only when the script is executed directly (e.g., `python app.py`)
    # and not when it's imported as a module.
    # Create the necessary directories for uploads and thumbnails if they don't exist.
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['THUMBNAIL_FOLDER'], exist_ok=True)
    # Start the Flask development server.
    # `debug=True` enables auto-reloading and provides detailed error pages.
    # `host='0.0.0.0'` makes the server accessible from any device on the network.
    app.run(debug=True, host='0.0.0.0')
