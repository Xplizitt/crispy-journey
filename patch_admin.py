import re

with open('part_lister/routes/admin.py', 'r') as f:
    content = f.read()

# Edit part_type for add_part route
content = content.replace("location = request.form.get('location', '')", "location = request.form.get('location', '')\n    part_type = request.form.get('part_type', 'Purchased')")
content = content.replace("INSERT INTO parts (barcode, description, part_number, uom, supplier_name, category, location, stock_quantity, reorder_level, notes)\n            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", "INSERT INTO parts (barcode, description, part_number, uom, supplier_name, category, location, stock_quantity, reorder_level, part_type, notes)\n            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")
content = content.replace("[barcode, description, part_number, uom, supplier_name, category, location, stock_quantity, reorder_level, notes]", "[barcode, description, part_number, uom, supplier_name, category, location, stock_quantity, reorder_level, part_type, notes]")


# Edit part_type for edit_part route POST
content = content.replace("location = request.form.get('location', '')\n        notes = request.form.get('notes', '')", "location = request.form.get('location', '')\n        part_type = request.form.get('part_type', 'Purchased')\n        notes = request.form.get('notes', '')")
content = content.replace("if old_part['location'] != location:", "if old_part['part_type'] != part_type:\n                changes.append(f\"Part type changed from '{old_part['part_type']}' to '{part_type}'\")\n            if old_part['location'] != location:")
content = content.replace("SET barcode=?, description=?, part_number=?, uom=?, supplier_name=?, category=?, location=?, stock_quantity=?, reorder_level=?, notes=?", "SET barcode=?, description=?, part_number=?, uom=?, supplier_name=?, category=?, location=?, stock_quantity=?, reorder_level=?, part_type=?, notes=?")

# In edit_part GET, pass bom_components
content = content.replace("cur = db.execute('SELECT * FROM attachments WHERE part_id = ?', [part_id])\n    attachments = cur.fetchall()\n\n    return render_template('edit_part.html', part=part, attachments=attachments)", "cur = db.execute('SELECT * FROM attachments WHERE part_id = ?', [part_id])\n    attachments = cur.fetchall()\n\n    cur = db.execute('''\n        SELECT bc.id, bc.child_part_id, p.barcode, p.description, p.part_number, bc.quantity_required\n        FROM bom_components bc\n        JOIN parts p ON bc.child_part_id = p.id\n        WHERE bc.parent_part_id = ?\n    ''', [part_id])\n    bom_components = cur.fetchall()\n\n    return render_template('edit_part.html', part=part, attachments=attachments, bom_components=bom_components)")


# In part_view GET, pass bom_components
content = content.replace("cur = db.execute('SELECT * FROM audit_log WHERE part_id = ? ORDER BY timestamp DESC', (part_id,))\n    audit_logs = cur.fetchall()\n\n    origin = request.args.get('origin', 'index')\n\n    return render_template('part_view.html', part=part, images=images, other_files=other_files, origin=origin, audit_logs=audit_logs)", "cur = db.execute('SELECT * FROM audit_log WHERE part_id = ? ORDER BY timestamp DESC', (part_id,))\n    audit_logs = cur.fetchall()\n\n    cur = db.execute('''\n        SELECT bc.id, bc.child_part_id, p.barcode, p.description, p.part_number, bc.quantity_required\n        FROM bom_components bc\n        JOIN parts p ON bc.child_part_id = p.id\n        WHERE bc.parent_part_id = ?\n    ''', [part_id])\n    bom_components = cur.fetchall()\n\n    origin = request.args.get('origin', 'index')\n\n    return render_template('part_view.html', part=part, images=images, other_files=other_files, origin=origin, audit_logs=audit_logs, bom_components=bom_components)")


# Append bom management routes and build_part route
new_routes = """
@admin_bp.route('/add_bom_component/<int:part_id>', methods=['POST'])
def add_bom_component(part_id):
    if not session.get('logged_in'):
        return redirect(url_for('admin_bp.login'))

    child_barcode = request.form.get('child_barcode')
    quantity_required = request.form.get('quantity_required')

    if not child_barcode or not quantity_required:
        flash('Barcode and quantity are required.', 'error')
        return redirect(url_for('admin_bp.edit_part', part_id=part_id))

    try:
        quantity_required = float(quantity_required)
    except ValueError:
        flash('Quantity must be a valid number.', 'error')
        return redirect(url_for('admin_bp.edit_part', part_id=part_id))

    db = get_db()

    cur = db.execute('SELECT id FROM parts WHERE barcode = ?', [child_barcode])
    child_part = cur.fetchone()

    if not child_part:
        flash(f'Child part with barcode {child_barcode} not found.', 'error')
        return redirect(url_for('admin_bp.edit_part', part_id=part_id))

    child_part_id = child_part['id']

    if child_part_id == part_id:
        flash('A part cannot be a component of itself.', 'error')
        return redirect(url_for('admin_bp.edit_part', part_id=part_id))

    db.execute('INSERT INTO bom_components (parent_part_id, child_part_id, quantity_required) VALUES (?, ?, ?)',
               [part_id, child_part_id, quantity_required])
    db.commit()
    flash('Component added successfully.')

    return redirect(url_for('admin_bp.edit_part', part_id=part_id))

@admin_bp.route('/remove_bom_component/<int:bom_id>', methods=['POST'])
def remove_bom_component(bom_id):
    if not session.get('logged_in'):
        return redirect(url_for('admin_bp.login'))

    parent_part_id = request.form.get('parent_part_id')

    db = get_db()
    db.execute('DELETE FROM bom_components WHERE id = ?', [bom_id])
    db.commit()
    flash('Component removed.')

    return redirect(url_for('admin_bp.edit_part', part_id=parent_part_id))

@admin_bp.route('/build_part/<int:part_id>', methods=['POST'])
def build_part(part_id):
    if not session.get('logged_in'):
         return redirect(url_for('admin_bp.login'))

    try:
        build_quantity = int(request.form.get('build_quantity', 1))
        if build_quantity <= 0:
            raise ValueError
    except ValueError:
        flash('Build quantity must be a positive integer.', 'error')
        return redirect(url_for('admin_bp.part_view', part_id=part_id))

    db = get_db()

    # Verify part exists
    cur = db.execute('SELECT part_number, description FROM parts WHERE id = ?', [part_id])
    parent_part = cur.fetchone()
    if not parent_part:
        flash('Part not found.', 'error')
        return redirect(url_for('admin_bp.admin'))

    # Get BOM
    cur = db.execute('''
        SELECT bc.child_part_id, bc.quantity_required, p.stock_quantity, p.barcode, p.description
        FROM bom_components bc
        JOIN parts p ON bc.child_part_id = p.id
        WHERE bc.parent_part_id = ?
    ''', [part_id])
    bom_components = cur.fetchall()

    if not bom_components:
        flash('This part has no BOM components. Cannot build.', 'error')
        return redirect(url_for('admin_bp.part_view', part_id=part_id))

    # Check stock
    insufficient_stock = []
    for comp in bom_components:
        total_required = comp['quantity_required'] * build_quantity
        if comp['stock_quantity'] < total_required:
            insufficient_stock.append(f"{comp['barcode']} ({comp['description']}) requires {total_required} but only has {comp['stock_quantity']}")

    if insufficient_stock:
        flash(f"Insufficient stock to build {build_quantity} unit(s): " + "; ".join(insufficient_stock), 'error')
        return redirect(url_for('admin_bp.part_view', part_id=part_id))

    try:
        # Deduct components
        for comp in bom_components:
            total_required = comp['quantity_required'] * build_quantity
            new_stock = comp['stock_quantity'] - total_required
            db.execute('UPDATE parts SET stock_quantity = ? WHERE id = ?', [new_stock, comp['child_part_id']])
            db.execute('INSERT INTO audit_log (part_id, action, details) VALUES (?, ?, ?)',
                       (comp['child_part_id'], 'Consumed', f"Consumed {total_required} units for assembly of Part {parent_part['part_number'] or parent_part['description']} (Built {build_quantity})"))

        # Increment parent
        db.execute('UPDATE parts SET stock_quantity = stock_quantity + ? WHERE id = ?', [build_quantity, part_id])
        db.execute('INSERT INTO audit_log (part_id, action, details) VALUES (?, ?, ?)',
                   (part_id, 'Built', f"Built {build_quantity} unit(s) from stock"))

        db.commit()
        flash(f'Successfully built {build_quantity} unit(s).', 'success')
    except Exception as e:
        db.rollback()
        flash(f'An error occurred during build: {e}', 'error')

    return redirect(url_for('admin_bp.part_view', part_id=part_id))
"""

content = content + "\n" + new_routes

with open('part_lister/routes/admin.py', 'w') as f:
    f.write(content)
