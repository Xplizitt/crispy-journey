# Part Lister - Database Initialization Script
#
# Project Overview:
# This script initializes the SQLite database for the Part Lister application.
# It defines the schema for the application's tables, including parts, lists, list_items, and attachments.
# Running this script directly will delete the existing database (if any) and create a new, empty one with the correct schema.
#
# Core Technologies:
# - Backend: Flask (Python)
# - Database: SQLite
#
# Notes for Future Agents:
# - Please update this header comment with any major changes or new requirements.
# - Be cautious when running this script, as it will delete all existing data.
# - If you need to modify the database schema, make the changes in this file and then run it to re-initialize the database.

import sqlite3
import os

# Get the absolute path to the directory where this script is located
_basedir = os.path.abspath(os.path.dirname(__file__))

# Define the path for the database file in the project root directory
DATABASE_PATH = os.path.join(_basedir, '..', 'parts.db')

def init_db_migrations(db):
    """
    Applies incremental schema changes to an existing database.
    This avoids dropping the database in production.
    """
    c = db.cursor()

    # Ensure parts table has new columns
    columns_to_add = {
        'category': 'TEXT',
        'location': 'TEXT',
        'stock_quantity': 'INTEGER DEFAULT 0',
        'reorder_level': 'INTEGER DEFAULT 0',
        'part_type': 'TEXT DEFAULT \'Purchased\''
    }

    c.execute("PRAGMA table_info(parts)")
    existing_columns = [row[1] for row in c.fetchall()]

    for col_name, col_type in columns_to_add.items():
        if col_name not in existing_columns:
            try:
                c.execute(f"ALTER TABLE parts ADD COLUMN {col_name} {col_type}")
            except sqlite3.OperationalError as e:
                print(f"Migration error (could be expected if column exists): {e}")

    # Ensure audit_log table exists
    c.execute('''
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            part_id INTEGER,
            action TEXT NOT NULL,
            details TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (part_id) REFERENCES parts (id) ON DELETE CASCADE
        )
    ''')


    # Ensure bom_components table exists
    c.execute('''
        CREATE TABLE IF NOT EXISTS bom_components (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_part_id INTEGER NOT NULL,
            child_part_id INTEGER NOT NULL,
            quantity_required REAL NOT NULL,
            FOREIGN KEY (parent_part_id) REFERENCES parts (id) ON DELETE CASCADE,
            FOREIGN KEY (child_part_id) REFERENCES parts (id)
        )
    ''')

    db.commit()


def init_db():
    # If the database file already exists, remove it to start fresh.
    if os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)

    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON") # Enforce foreign key constraints

    # Create parts table
    c.execute('''
        CREATE TABLE parts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode TEXT NOT NULL UNIQUE,
            description TEXT NOT NULL,
            part_number TEXT,
            uom TEXT,
            supplier_name TEXT,
            category TEXT,
            location TEXT,
            stock_quantity INTEGER DEFAULT 0,
            reorder_level INTEGER DEFAULT 0,
            part_type TEXT DEFAULT 'Purchased',
            thumbnail TEXT,
            notes TEXT
        )
    ''')

    # Create lists table
    c.execute('''
        CREATE TABLE lists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')

    # Create list_items table to store items for multiple lists
    c.execute('''
        CREATE TABLE list_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            list_id INTEGER NOT NULL,
            part_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (part_id) REFERENCES parts (id),
            FOREIGN KEY (list_id) REFERENCES lists (id) ON DELETE CASCADE
        )
    ''')

    # Seed a default list
    c.execute("INSERT INTO lists (name) VALUES (?)", ['Default List'])

    # Create attachments table
    c.execute('''
        CREATE TABLE attachments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            part_id INTEGER,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            FOREIGN KEY (part_id) REFERENCES parts (id) ON DELETE SET NULL
        )
    ''')

        # Create bom_components table
    c.execute('''
        CREATE TABLE bom_components (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_part_id INTEGER NOT NULL,
            child_part_id INTEGER NOT NULL,
            quantity_required REAL NOT NULL,
            FOREIGN KEY (parent_part_id) REFERENCES parts (id) ON DELETE CASCADE,
            FOREIGN KEY (child_part_id) REFERENCES parts (id)
        )
    ''')

    # Create audit_log table
    c.execute('''
        CREATE TABLE audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            part_id INTEGER,
            action TEXT NOT NULL,
            details TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (part_id) REFERENCES parts (id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print(f"Database initialized successfully at: {DATABASE_PATH}")
