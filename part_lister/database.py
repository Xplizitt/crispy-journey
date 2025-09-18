# ==================================================================================================
# Part Lister - Database Initialization Script
# ==================================================================================================
#
# Author: AI Agent (Initial development)
# Date: 2025-09-17
#
# ## Script Overview:
# This script is responsible for initializing the SQLite database for the Part Lister application.
# It defines the complete database schema, including all tables, columns, constraints, and
# relationships. Running this script is a destructive operation: it will delete the
# existing database file (if any) and create a new, empty one with the correct schema
# and a single "Default List".
#
# ## How to Use:
# To initialize or reset the database, run this script from the command line:
# `python part_lister/database.py`
#
# ## Database Schema:
# - `parts`: The central table for all parts and assemblies.
#   - `is_assembly`: A boolean flag (0 or 1) to distinguish between regular parts and assemblies.
# - `assembly_parts`: A link table to define the many-to-many relationship between an assembly
#   (a `part`) and its constituent `parts`.
# - `lists`: Stores the names of the different picking lists.
# - `list_items`: A link table that connects a `part` to a `list` with a specific quantity.
# - `attachments`: Stores metadata for all uploaded files, linked to a `part`.
#   - `ON DELETE SET NULL`: If a part is deleted, its attachments are not deleted. Instead,
#     their `part_id` is set to NULL, making them "unassigned".
#
# ## Notes for Future Agents:
# - **Destructive Operation:** Be extremely cautious when running this script, as it will
#   erase all data in the database.
# - **Schema Migrations:** This project does not have a formal migration system. If you need
#   to alter the schema, you must update the `CREATE TABLE` statements in this file and
#   then re-run the script. This is only suitable for development environments.
#
# ## Recent Changes:
# - 2025-09-17: (AI Agent) Added comprehensive header documentation to improve clarity.
# - 2025-09-16: (Previous Agent) Added support for assemblies, including the 'is_assembly'
#   flag and the 'assembly_parts' table.

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
