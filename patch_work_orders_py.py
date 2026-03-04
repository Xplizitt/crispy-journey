def patch_wo():
    with open('part_lister/routes/work_orders.py', 'r') as f:
        content = f.read()

    # Index route
    content = content.replace("cur = db.execute('SELECT * FROM work_orders ORDER BY created_at DESC')", "cur = db.execute('''SELECT w.*, c.name as customer_name FROM work_orders w LEFT JOIN customers c ON w.customer_id = c.id ORDER BY w.created_at DESC''')")
    content = content.replace("return render_template('work_orders/index.html', work_orders=work_orders)", "cur_cust = db.execute('SELECT id, name FROM customers ORDER BY name ASC')\n    customers = cur_cust.fetchall()\n    return render_template('work_orders/index.html', work_orders=work_orders, customers=customers)")

    # Create route
    content = content.replace("description = request.form.get('description')", "description = request.form.get('description')\n    customer_id = request.form.get('customer_id')\n    if not customer_id: customer_id = None")
    content = content.replace("db.execute('INSERT INTO work_orders (title, description) VALUES (?, ?)', [title, description])", "db.execute('INSERT INTO work_orders (title, description, customer_id) VALUES (?, ?, ?)', [title, description, customer_id])")

    # View route
    content = content.replace("cur = db.execute('SELECT * FROM work_orders WHERE id = ?', [work_order_id])", "cur = db.execute('''SELECT w.*, c.name as customer_name FROM work_orders w LEFT JOIN customers c ON w.customer_id = c.id WHERE w.id = ?''', [work_order_id])")

    with open('part_lister/routes/work_orders.py', 'w') as f:
        f.write(content)

patch_wo()
