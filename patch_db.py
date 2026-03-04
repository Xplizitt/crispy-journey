import sqlite3

def patch_database():
    with open('part_lister/database.py', 'r') as f:
        content = f.read()

    migration_code = """
    # Ensure customers table exists
    c.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            address TEXT,
            notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Add customer_id to parts if it doesn't exist
    c.execute("PRAGMA table_info(parts)")
    existing_columns = [row[1] for row in c.fetchall()]
    if 'customer_id' not in existing_columns:
        try:
            c.execute("ALTER TABLE parts ADD COLUMN customer_id INTEGER REFERENCES customers(id)")
        except sqlite3.OperationalError as e:
            pass

    # Add customer_id to work_orders if it doesn't exist
    c.execute("PRAGMA table_info(work_orders)")
    existing_columns = [row[1] for row in c.fetchall()]
    if 'customer_id' not in existing_columns:
        try:
            c.execute("ALTER TABLE work_orders ADD COLUMN customer_id INTEGER REFERENCES customers(id)")
        except sqlite3.OperationalError as e:
            pass
"""
    if "CREATE TABLE IF NOT EXISTS customers" not in content:
        content = content.replace("    db.commit()", migration_code + "\n    db.commit()", 1)

        init_db_code = """
    # Create customers table
    c.execute('''
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            address TEXT,
            notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
"""
        # Also need to add customer_id to parts table create
        content = content.replace("thumbnail TEXT,", "customer_id INTEGER REFERENCES customers(id),\n            thumbnail TEXT,")
        content = content.replace("notes TEXT\n        )", "notes TEXT\n        )")

        # Also need to add customer_id to work_orders table create
        content = content.replace("status TEXT DEFAULT 'Open',", "customer_id INTEGER REFERENCES customers(id),\n            status TEXT DEFAULT 'Open',")

        content = content.replace("    # Create lists table", init_db_code + "\n    # Create lists table", 1)

        with open('part_lister/database.py', 'w') as f:
            f.write(content)

patch_database()
