import sqlite3

def init_db():
    conn = sqlite3.connect('parts.db')
    c = conn.cursor()

    # Drop tables if they exist to start fresh
    c.execute('DROP TABLE IF EXISTS parts')
    c.execute('DROP TABLE IF EXISTS list_items')

    # Create parts table
    c.execute('''
        CREATE TABLE parts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode TEXT NOT NULL UNIQUE,
            description TEXT NOT NULL,
            part_number TEXT,
            uom TEXT,
            supplier_name TEXT
        )
    ''')

    # Create list_items table to store the current list
    c.execute('''
        CREATE TABLE list_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            part_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (part_id) REFERENCES parts (id)
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized.")
