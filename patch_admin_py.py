def patch_admin():
    with open('part_lister/routes/admin.py', 'r') as f:
        content = f.read()

    # Admin index route
    content = content.replace("categories = [row['category'] for row in cur.fetchall()]", "categories = [row['category'] for row in cur.fetchall()]\n    \n    cur = db.execute('SELECT id, name FROM customers ORDER BY name ASC')\n    customers = cur.fetchall()")
    content = content.replace("return render_template('admin.html', parts=parts, search_query=search_query, categories=categories, current_category=category_filter)", "return render_template('admin.html', parts=parts, search_query=search_query, categories=categories, current_category=category_filter, customers=customers)")

    # Edit part GET route (we need to pass customers to edit_part.html)
    content = content.replace("cur = db.execute('''\n        SELECT id, filename\n        FROM attachments\n        WHERE part_id = ?\n    ''', [part_id])\n    attachments = cur.fetchall()", "cur = db.execute('''\n        SELECT id, filename\n        FROM attachments\n        WHERE part_id = ?\n    ''', [part_id])\n    attachments = cur.fetchall()\n    \n    cur = db.execute('SELECT id, name FROM customers ORDER BY name ASC')\n    customers = cur.fetchall()")
    content = content.replace("return render_template('edit_part.html', part=part, attachments=attachments, parts_for_bom=parts_for_bom, bom_components=bom_components)", "return render_template('edit_part.html', part=part, attachments=attachments, parts_for_bom=parts_for_bom, bom_components=bom_components, customers=customers)")

    # Add part POST route
    content = content.replace("location = request.form.get('location', '')\n    part_type = request.form.get('part_type', 'Purchased')", "location = request.form.get('location', '')\n    part_type = request.form.get('part_type', 'Purchased')\n    customer_id = request.form.get('customer_id')\n    if not customer_id: customer_id = None")
    content = content.replace("INSERT INTO parts (barcode, description, part_number, uom, supplier_name, category, location, stock_quantity, reorder_level, part_type, notes)\n            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", "INSERT INTO parts (barcode, description, part_number, uom, supplier_name, category, location, stock_quantity, reorder_level, part_type, customer_id, notes)\n            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")
    content = content.replace("[barcode, description, part_number, uom, supplier_name, category, location, stock_quantity, reorder_level, part_type, notes]", "[barcode, description, part_number, uom, supplier_name, category, location, stock_quantity, reorder_level, part_type, customer_id, notes]")

    # Edit part POST route
    content = content.replace("location = request.form.get('location', '')\n        part_type = request.form.get('part_type', 'Purchased')\n        notes = request.form.get('notes', '')", "location = request.form.get('location', '')\n        part_type = request.form.get('part_type', 'Purchased')\n        notes = request.form.get('notes', '')\n        customer_id = request.form.get('customer_id')\n        if not customer_id: customer_id = None")
    content = content.replace("SET barcode=?, description=?, part_number=?, uom=?, supplier_name=?, category=?, location=?, stock_quantity=?, reorder_level=?, part_type=?, notes=?\n                WHERE id=?", "SET barcode=?, description=?, part_number=?, uom=?, supplier_name=?, category=?, location=?, stock_quantity=?, reorder_level=?, part_type=?, customer_id=?, notes=?\n                WHERE id=?")
    content = content.replace("[barcode, description, part_number, uom, supplier_name, category, location, stock_quantity, reorder_level, part_type, notes, part_id]", "[barcode, description, part_number, uom, supplier_name, category, location, stock_quantity, reorder_level, part_type, customer_id, notes, part_id]")

    # Part view GET route (fetch customer name)
    content = content.replace("cur = db.execute('SELECT * FROM parts WHERE id = ?', [part_id])\n    part = cur.fetchone()", "cur = db.execute('''SELECT p.*, c.name as customer_name FROM parts p LEFT JOIN customers c ON p.customer_id = c.id WHERE p.id = ?''', [part_id])\n    part = cur.fetchone()")

    with open('part_lister/routes/admin.py', 'w') as f:
        f.write(content)

patch_admin()
