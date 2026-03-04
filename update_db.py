import sqlite3

db = sqlite3.connect('parts.db')
c = db.cursor()

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

# Add customer_id to parts
try:
    c.execute("ALTER TABLE parts ADD COLUMN customer_id INTEGER REFERENCES customers(id)")
except sqlite3.OperationalError:
    pass

# Add customer_id to work_orders
try:
    c.execute("ALTER TABLE work_orders ADD COLUMN customer_id INTEGER REFERENCES customers(id)")
except sqlite3.OperationalError:
    pass

db.commit()
db.close()
