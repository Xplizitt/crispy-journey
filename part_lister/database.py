import sqlite3
import os

# Get the absolute path to the directory where this script is located
_basedir = os.path.abspath(os.path.dirname(__file__))

# Define the path for the database file in the project root directory
DATABASE_PATH = os.path.join(_basedir, '..', 'parts.db')

def init_db():
    # If the database file already exists, remove it to start fresh.
    if os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)

    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()

    # Create parts table
    c.execute('''
        CREATE TABLE parts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode TEXT NOT NULL UNIQUE,
            description TEXT NOT NULL,
            part_number TEXT,
            uom TEXT,
            supplier_name TEXT,
            thumbnail TEXT
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

    # Create attachments table
    c.execute('''
        CREATE TABLE attachments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            part_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            FOREIGN KEY (part_id) REFERENCES parts (id)
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print(f"Database initialized successfully at: {DATABASE_PATH}")
