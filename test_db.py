import sqlite3
db = sqlite3.connect('../parts.db')
print("parts table columns:")
print([row[1] for row in db.execute('PRAGMA table_info(parts)')])
print("work_orders table columns:")
print([row[1] for row in db.execute('PRAGMA table_info(work_orders)')])
print("customers table columns:")
print([row[1] for row in db.execute('PRAGMA table_info(customers)')])
