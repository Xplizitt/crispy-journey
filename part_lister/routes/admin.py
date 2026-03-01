# Mile Marker: 2025-09-16 - Extracted admin routes to admin_bp blueprint.

from flask import Blueprint, render_template, request, session, g, flash, redirect, url_for, send_from_directory, Response
from flask import current_app as app
from werkzeug.utils import secure_filename
import sqlite3
import os
import csv
import io

# Utility functions imported or defined here as needed
# Using app.config logic here isn't strictly necessary for blueprints definition, but when called
# app context is active
def get_db():
    if not hasattr(g, 'sqlite_db'):
        db_path = app.config['DATABASE']
        g.sqlite_db = sqlite3.connect(db_path)
        g.sqlite_db.row_factory = sqlite3.Row
    return g.sqlite_db

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'zip', 'rar', '7z', 'cad', 'dxf'}
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'zip', 'rar', '7z', 'cad', 'dxf'}
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'zip', 'rar', '7z', 'cad', 'dxf'}
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'zip', 'rar', '7z', 'cad', 'dxf'}
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'zip', 'rar', '7z', 'cad', 'dxf'}
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'zip', 'rar', '7z', 'cad', 'dxf'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

admin_bp = Blueprint('admin_bp', __name__)

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        # ADMIN_PASSWORD needs to be accessed, assuming it's admin. Better to put in app config or local
        if request.form['password'] == 'admin':
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('admin_bp.admin'))
        else:
            error = 'Invalid password'
    return render_template('login.html', error=error)

@admin_bp.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('core_bp.index'))

@admin_bp.route('/admin')
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('admin_bp.login'))

    search_query = request.args.get('search', '').strip()
    category_filter = request.args.get('category', '').strip()

    db = get_db()

    # Base query for parts
    query = 'SELECT * FROM parts WHERE 1=1'
    params = []

    if search_query:
        query += ' AND (barcode LIKE ? OR description LIKE ? OR part_number LIKE ?)'
        wildcard_search = f'%{search_query}%'
        params.extend([wildcard_search, wildcard_search, wildcard_search])

    if category_filter:
         query += ' AND category = ?'
         params.append(category_filter)

    query += ' ORDER BY id DESC'

    cur = db.execute(query, params)
    parts = cur.fetchall()

    # Get distinct categories for the filter dropdown
    cur = db.execute('SELECT DISTINCT category FROM parts WHERE category IS NOT NULL AND category != "" ORDER BY category')
    categories = [row['category'] for row in cur.fetchall()]

    return render_template('admin.html', parts=parts, search_query=search_query, categories=categories, current_category=category_filter)

@admin_bp.route('/add_part', methods=['POST'])
def add_part():
    if not session.get('logged_in'):
        return redirect(url_for('admin_bp.login'))

    barcode = request.form['barcode']
    description = request.form['description']
    part_number = request.form['part_number']
    uom = request.form['uom']
    supplier_name = request.form['supplier_name']
    category = request.form.get('category', '')
    location = request.form.get('location', '')

    try:
        stock_quantity = int(request.form.get('stock_quantity', 0))
        reorder_level = int(request.form.get('reorder_level', 0))
    except ValueError:
        flash('Stock and Reorder quantities must be numbers.', 'error')
        return redirect(url_for('admin_bp.admin'))

    notes = request.form.get('notes', '')

    db = get_db()
    try:
        cur = db.execute('''
            INSERT INTO parts (barcode, description, part_number, uom, supplier_name, category, location, stock_quantity, reorder_level, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', [barcode, description, part_number, uom, supplier_name, category, location, stock_quantity, reorder_level, notes])

        part_id = cur.lastrowid

        # Log creation
        db.execute('INSERT INTO audit_log (part_id, action, details) VALUES (?, ?, ?)',
                   (part_id, 'Created', f"Part created with barcode: {barcode}"))

        # Handle file uploads
        if 'files' in request.files:
            files = request.files.getlist('files')
            for file in files:
                if file.filename == '':
                    continue
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    db.execute('INSERT INTO attachments (part_id, filename, filepath) VALUES (?, ?, ?)',
                               [part_id, filename, filename])
                    db.execute('INSERT INTO audit_log (part_id, action, details) VALUES (?, ?, ?)',
                               (part_id, 'Attachment Added', f"Added file: {filename}"))

        db.commit()
        flash('New part was successfully added')
    except sqlite3.IntegrityError:
        flash('Error: Barcode already exists')

    return redirect(url_for('admin_bp.admin'))

@admin_bp.route('/edit_part/<int:part_id>', methods=['GET', 'POST'])
def edit_part(part_id):
    if not session.get('logged_in'):
        return redirect(url_for('admin_bp.login'))

    db = get_db()

    if request.method == 'POST':
        barcode = request.form['barcode']
        description = request.form['description']
        part_number = request.form['part_number']
        uom = request.form['uom']
        supplier_name = request.form['supplier_name']
        category = request.form.get('category', '')
        location = request.form.get('location', '')
        notes = request.form.get('notes', '')

        try:
            stock_quantity = int(request.form.get('stock_quantity', 0))
            reorder_level = int(request.form.get('reorder_level', 0))
        except ValueError:
            flash('Stock and Reorder quantities must be numbers.', 'error')
            return redirect(url_for('admin_bp.edit_part', part_id=part_id))

        try:
            # Get old values for logging
            cur = db.execute('SELECT * FROM parts WHERE id = ?', (part_id,))
            old_part = cur.fetchone()

            changes = []
            if old_part['stock_quantity'] != stock_quantity:
                changes.append(f"Stock changed from {old_part['stock_quantity']} to {stock_quantity}")
            if old_part['location'] != location:
                changes.append(f"Location changed from '{old_part['location']}' to '{location}'")

            db.execute('''
                UPDATE parts
                SET barcode=?, description=?, part_number=?, uom=?, supplier_name=?, category=?, location=?, stock_quantity=?, reorder_level=?, notes=?
                WHERE id=?
            ''', [barcode, description, part_number, uom, supplier_name, category, location, stock_quantity, reorder_level, notes, part_id])

            if changes:
                db.execute('INSERT INTO audit_log (part_id, action, details) VALUES (?, ?, ?)',
                          (part_id, 'Updated', "; ".join(changes)))

            # Handle new file uploads during edit
            if 'files' in request.files:
                files = request.files.getlist('files')
                for file in files:
                    if file.filename == '':
                        continue
                    if file and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        file.save(filepath)
                        db.execute('INSERT INTO attachments (part_id, filename, filepath) VALUES (?, ?, ?)',
                                   [part_id, filename, filename])
                        db.execute('INSERT INTO audit_log (part_id, action, details) VALUES (?, ?, ?)',
                                   (part_id, 'Attachment Added', f"Added file: {filename}"))

            db.commit()
            flash('Part successfully updated')
            return redirect(url_for('admin_bp.admin'))
        except sqlite3.IntegrityError:
            flash('Error: Barcode already exists')

    cur = db.execute('SELECT * FROM parts WHERE id = ?', [part_id])
    part = cur.fetchone()

    if part is None:
        flash('Part not found')
        return redirect(url_for('admin_bp.admin'))

    cur = db.execute('SELECT * FROM attachments WHERE part_id = ?', [part_id])
    attachments = cur.fetchall()

    return render_template('edit_part.html', part=part, attachments=attachments)

@admin_bp.route('/part/<int:part_id>')
def part_view(part_id):
    db = get_db()
    cur = db.execute('SELECT * FROM parts WHERE id = ?', [part_id])
    part = cur.fetchone()

    if part is None:
        flash('Part not found', 'error')
        return redirect(url_for('admin_bp.admin'))

    cur = db.execute('SELECT * FROM attachments WHERE part_id = ?', [part_id])
    attachments = cur.fetchall()

    images = []
    other_files = []
    for attachment in attachments:
        filename = attachment['filename'].lower()
        if filename.endswith(('.png', '.jpg', '.jpeg', '.gif')):
            images.append(attachment)
        else:
            other_files.append(attachment)

    cur = db.execute('SELECT * FROM audit_log WHERE part_id = ? ORDER BY timestamp DESC', (part_id,))
    audit_logs = cur.fetchall()

    origin = request.args.get('origin', 'index')

    return render_template('part_view.html', part=part, images=images, other_files=other_files, origin=origin, audit_logs=audit_logs)

@admin_bp.route('/set_thumbnail/<int:part_id>/<int:attachment_id>')
def set_thumbnail(part_id, attachment_id):
    if not session.get('logged_in'):
        return redirect(url_for('admin_bp.login'))

    db = get_db()
    cur = db.execute('SELECT filename FROM attachments WHERE id = ? AND part_id = ?', [attachment_id, part_id])
    attachment = cur.fetchone()

    if attachment:
        original_filename = attachment['filename']
        # Don't try to thumbnail CAD files
        if not original_filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            flash('Only image files can be set as thumbnails.')
            return redirect(url_for('admin_bp.edit_part', part_id=part_id))

        _delete_part_thumbnail_file(part_id)

        thumb_filename = f"thumb_{part_id}_{original_filename}"
        original_path = os.path.join(app.config['UPLOAD_FOLDER'], original_filename)
        thumb_path = os.path.join(app.config['THUMBNAIL_FOLDER'], thumb_filename)

        from part_lister.app import create_thumbnail
        if create_thumbnail(original_path, thumb_path):
            db.execute('UPDATE parts SET thumbnail = ? WHERE id = ?', [thumb_filename, part_id])
            db.commit()
            flash('Thumbnail set successfully.')
        else:
            flash('Failed to create thumbnail. Ensure the file is a valid image.')
    else:
        flash('Attachment not found.')

    return redirect(url_for('admin_bp.edit_part', part_id=part_id))

@admin_bp.route('/clear_thumbnail/<int:part_id>')
def clear_thumbnail(part_id):
    if not session.get('logged_in'):
        return redirect(url_for('admin_bp.login'))

    _delete_part_thumbnail_file(part_id)

    db = get_db()
    db.execute('UPDATE parts SET thumbnail = NULL WHERE id = ?', [part_id])
    db.commit()
    flash('Thumbnail cleared.')
    return redirect(url_for('admin_bp.edit_part', part_id=part_id))

@admin_bp.route('/delete_attachment/<int:attachment_id>')
def delete_attachment(attachment_id):
    if not session.get('logged_in'):
        return redirect(url_for('admin_bp.login'))

    db = get_db()
    cur = db.execute('SELECT part_id, filename FROM attachments WHERE id = ?', [attachment_id])
    attachment = cur.fetchone()

    if attachment:
        part_id = attachment['part_id']
        filename = attachment['filename']

        # Check if this file is the thumbnail.
        cur = db.execute('SELECT thumbnail FROM parts WHERE id = ?', [part_id])
        part = cur.fetchone()

        if part and part['thumbnail'] and filename in part['thumbnail']:
             flash('Cannot delete this attachment because it is currently used as the thumbnail. Please clear the thumbnail first.')
             return redirect(url_for('admin_bp.edit_part', part_id=part_id))

        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        except OSError as e:
             # File might already be gone, or we might not have permission. Log it but continue.
             print(f"Error removing file {filename}: {e}")

        db.execute('DELETE FROM attachments WHERE id = ?', [attachment_id])
        db.execute('INSERT INTO audit_log (part_id, action, details) VALUES (?, ?, ?)',
                   (part_id, 'Attachment Removed', f"Removed file: {filename}"))
        db.commit()
        flash('Attachment deleted.')
        return redirect(url_for('admin_bp.edit_part', part_id=part_id))
    else:
        flash('Attachment not found.')
        return redirect(url_for('admin_bp.admin'))

@admin_bp.route('/apply_thumbnail/<filename>')
def apply_thumbnail(filename):
    if not session.get('logged_in'):
        return redirect(url_for('admin_bp.login'))

    part_ids_str = request.args.get('part_ids', '')
    if not part_ids_str:
        flash("No parts selected.")
        return redirect(url_for('admin_bp.admin'))

    part_ids = [int(pid) for pid in part_ids_str.split(',') if pid]

    db = get_db()
    success_count = 0
    from part_lister.app import create_thumbnail
    for part_id in part_ids:
        # 1. Delete existing thumbnail file if it exists
        _delete_part_thumbnail_file(part_id)

        # 2. Create new thumbnail
        thumb_filename = f"thumb_{part_id}_{filename}"
        original_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        thumb_path = os.path.join(app.config['THUMBNAIL_FOLDER'], thumb_filename)

        if create_thumbnail(original_path, thumb_path):
             # 3. Update database
             db.execute('UPDATE parts SET thumbnail = ? WHERE id = ?', [thumb_filename, part_id])
             success_count += 1

    db.commit()

    if success_count > 0:
        flash(f'Thumbnail applied to {success_count} part(s).')
    else:
        flash('Failed to apply thumbnail.')

    if len(part_ids) == 1:
        return redirect(url_for('admin_bp.edit_part', part_id=part_ids[0]))
    return redirect(url_for('admin_bp.admin'))

@admin_bp.route('/select_thumbnail')
def select_thumbnail():
    if not session.get('logged_in'):
        return redirect(url_for('admin_bp.login'))

    part_ids = request.args.get('part_ids')
    if not part_ids:
        flash("No parts specified.")
        return redirect(url_for('admin_bp.admin'))

    db = get_db()
    cur = db.execute('''
        SELECT id, filename FROM attachments
        WHERE filename LIKE '%.jpg' OR filename LIKE '%.jpeg' OR filename LIKE '%.png' OR filename LIKE '%.gif'
        ORDER BY id DESC
    ''')
    images = cur.fetchall()
    return render_template('select_thumbnail.html', images=images, part_ids=part_ids)

def _delete_part_thumbnail_file(part_id):
    """Helper function to delete the actual thumbnail file for a given part ID."""
    db = get_db()
    cur = db.execute('SELECT thumbnail FROM parts WHERE id = ?', [part_id])
    part = cur.fetchone()
    if part and part['thumbnail']:
        thumb_path = os.path.join(app.config['THUMBNAIL_FOLDER'], part['thumbnail'])
        try:
            if os.path.exists(thumb_path):
                os.remove(thumb_path)
        except OSError as e:
            print(f"Error removing thumbnail file {part['thumbnail']}: {e}")

@admin_bp.route('/bulk_edit', methods=['POST'])
def bulk_edit():
    if not session.get('logged_in'):
        return redirect(url_for('admin_bp.login'))

    action = request.form.get('action')
    selected_parts = request.form.getlist('selected_parts')

    if not selected_parts:
        flash('No parts selected.')
        return redirect(url_for('admin_bp.admin'))

    if action == 'delete':
        db = get_db()
        for part_id in selected_parts:
            # First, handle thumbnail deletion
            _delete_part_thumbnail_file(part_id)

            # Note: The database schema uses ON DELETE SET NULL for attachments,
            # so the attachment records will remain, but their part_id will be NULL.
            # We also need to delete the actual files for these attachments?
            # For now, let's just let the DB handle the record, the file remains in uploads.

            db.execute('DELETE FROM parts WHERE id = ?', [part_id])
        db.commit()
        flash(f'Successfully deleted {len(selected_parts)} parts.')

    elif action == 'set_thumbnail':
         # Pass the list of part IDs to the gallery selection view
         part_ids_str = ','.join(selected_parts)
         return redirect(url_for('admin_bp.select_thumbnail', part_ids=part_ids_str))

    return redirect(url_for('admin_bp.admin'))

@admin_bp.route('/delete_part/<int:part_id>')
def delete_part(part_id):
    if not session.get('logged_in'):
        return redirect(url_for('admin_bp.login'))

    _delete_part_thumbnail_file(part_id)

    db = get_db()
    db.execute('DELETE FROM parts WHERE id = ?', [part_id])
    db.commit()
    flash('Part deleted')
    return redirect(url_for('admin_bp.admin'))

@admin_bp.route('/export_parts')
def export_parts():
    if not session.get('logged_in'):
         return redirect(url_for('admin_bp.login'))

    db = get_db()
    search_query = request.args.get('search', '').strip()
    category_filter = request.args.get('category', '').strip()

    query = 'SELECT barcode, description, part_number, uom, supplier_name, category, location, stock_quantity, reorder_level, notes FROM parts WHERE 1=1'
    params = []

    if search_query:
        query += ' AND (barcode LIKE ? OR description LIKE ? OR part_number LIKE ?)'
        wildcard_search = f'%{search_query}%'
        params.extend([wildcard_search, wildcard_search, wildcard_search])
    if category_filter:
         query += ' AND category = ?'
         params.append(category_filter)

    cur = db.execute(query, params)
    parts = cur.fetchall()

    # Create a string buffer to write CSV data
    si = io.StringIO()
    cw = csv.writer(si)
    # Write headers
    cw.writerow(['Barcode', 'Description', 'Part Number', 'UOM', 'Supplier', 'Category', 'Location', 'Stock Qty', 'Reorder Level', 'Notes'])

    for p in parts:
        cw.writerow([
            p['barcode'], p['description'], p['part_number'], p['uom'],
            p['supplier_name'], p['category'], p['location'],
            p['stock_quantity'], p['reorder_level'], p['notes']
        ])

    output = si.getvalue()
    si.close()

    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=parts_export.csv"}
    )

@admin_bp.route('/import_parts', methods=['POST'])
def import_parts():
    if not session.get('logged_in'):
        return redirect(url_for('admin_bp.login'))

    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('admin_bp.admin'))
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('admin_bp.admin'))

    if file and file.filename.endswith('.csv'):
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.reader(stream)

        headers = next(csv_input, None)
        if not headers or 'Barcode' not in headers:
             flash('Invalid CSV format. Must include a "Barcode" column header.', 'error')
             return redirect(url_for('admin_bp.admin'))

        # Create a mapping of expected column names to their index
        header_map = {name.lower().strip(): idx for idx, name in enumerate(headers)}

        db = get_db()
        success_count = 0
        error_count = 0

        for row in csv_input:
            try:
                # Helper to safely get value by column name or default
                def get_val(col_name, default=''):
                    idx = header_map.get(col_name.lower())
                    return row[idx] if idx is not None and idx < len(row) else default

                barcode = get_val('barcode')
                if not barcode:
                    error_count += 1
                    continue

                description = get_val('description', 'Imported Part')
                part_number = get_val('part_number', '')
                uom = get_val('uom', '')
                supplier_name = get_val('supplier', '') # 'supplier' or 'supplier_name' based on export
                if not supplier_name: supplier_name = get_val('supplier name', '')
                category = get_val('category', '')
                location = get_val('location', '')

                try:
                    stock_qty = int(get_val('stock qty', 0) or get_val('stock_quantity', 0))
                except ValueError: stock_qty = 0

                try:
                    reorder_lvl = int(get_val('reorder level', 0) or get_val('reorder_level', 0))
                except ValueError: reorder_lvl = 0

                notes = get_val('notes', '')

                db.execute('''
                    INSERT INTO parts (barcode, description, part_number, uom, supplier_name, category, location, stock_quantity, reorder_level, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', [barcode, description, part_number, uom, supplier_name, category, location, stock_qty, reorder_lvl, notes])
                success_count += 1
            except sqlite3.IntegrityError:
                # Skip existing barcodes
                error_count += 1
            except Exception as e:
                print(f"Error importing row: {e}")
                error_count += 1

        db.commit()
        flash(f'Successfully imported {success_count} parts. Skipped {error_count} parts (duplicates or missing data).')
    else:
        flash('Invalid file type. Please upload a CSV.')

    return redirect(url_for('admin_bp.admin'))

@admin_bp.route('/gallery', methods=['GET', 'POST'])
def gallery():
    if not session.get('logged_in'):
        return redirect(url_for('admin_bp.login'))

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
        return redirect(url_for('admin_bp.gallery'))

    cur = db.execute('''
        SELECT id, filename FROM attachments
        WHERE filename LIKE '%.jpg' OR filename LIKE '%.jpeg' OR filename LIKE '%.png' OR filename LIKE '%.gif'
        ORDER BY id DESC
    ''')
    images = cur.fetchall()
    return render_template('gallery.html', images=images)

@admin_bp.route('/delete_image/<int:image_id>')
def delete_image(image_id):
    if not session.get('logged_in'):
        return redirect(url_for('admin_bp.login'))
    db = get_db()
    cur = db.execute('SELECT filename FROM attachments WHERE id = ?', [image_id])
    image = cur.fetchone()
    if not image:
        flash('Image not found.')
        return redirect(url_for('admin_bp.gallery'))

    # Check if this image is used as a thumbnail
    thumb_filename_pattern = f"%thumb_%_{image['filename']}"
    cur = db.execute('SELECT COUNT(*) as count FROM parts WHERE thumbnail LIKE ?', [thumb_filename_pattern])
    usage = cur.fetchone()
    if usage['count'] > 0:
        flash(f"Cannot delete image. It is currently used as a thumbnail for {usage['count']} part(s). Please assign a different thumbnail to those parts first.")
        return redirect(url_for('admin_bp.gallery'))

    # Delete file from uploads folder
    try:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], image['filename']))
    except OSError as e:
        flash(f"Error deleting file from filesystem: {e}")

    # Delete record from database
    db.execute('DELETE FROM attachments WHERE id = ?', [image_id])
    db.commit()
    flash(f"Image '{image['filename']}' deleted successfully.")
    return redirect(url_for('admin_bp.gallery'))
