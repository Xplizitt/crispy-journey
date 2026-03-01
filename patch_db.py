import re

with open('part_lister/database.py', 'r') as f:
    content = f.read()

# Add part_type to columns_to_add
content = content.replace("'reorder_level': 'INTEGER DEFAULT 0'", "'reorder_level': 'INTEGER DEFAULT 0',\n        'part_type': 'TEXT DEFAULT \\'Purchased\\''")

# Add bom_components table
new_table_sql = """
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
"""
content = content.replace("db.commit()\n\n\ndef init_db():", f"{new_table_sql}\n\ndef init_db():")

# Update init_db part creation
init_parts_sql = """            reorder_level INTEGER DEFAULT 0,
            part_type TEXT DEFAULT 'Purchased',
            thumbnail TEXT,"""
content = content.replace("reorder_level INTEGER DEFAULT 0,\n            thumbnail TEXT,", init_parts_sql)

init_bom_sql = """    # Create bom_components table
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

    # Create audit_log table"""
content = content.replace("# Create audit_log table", init_bom_sql)

with open('part_lister/database.py', 'w') as f:
    f.write(content)
