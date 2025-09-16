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
# - 2025-09-16: Added support for assemblies, including the 'is_assembly' flag and the 'assembly_parts' table.

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
            thumbnail TEXT,
            notes TEXT,
            is_assembly INTEGER NOT NULL DEFAULT 0
        )
    ''')

    # Create assembly_parts table
    c.execute('''
        CREATE TABLE assembly_parts (
            assembly_id INTEGER NOT NULL,
            part_id INTEGER NOT NULL,
            PRIMARY KEY (assembly_id, part_id),
            FOREIGN KEY (assembly_id) REFERENCES parts (id) ON DELETE CASCADE,
            FOREIGN KEY (part_id) REFERENCES parts (id) ON DELETE CASCADE
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

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print(f"Database initialized successfully at: {DATABASE_PATH}")
