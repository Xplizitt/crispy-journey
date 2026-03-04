Learnings:
- When modifying Flask Blueprints with sqlite3, always ensure `db.commit()` is called after data modification (`INSERT`, `UPDATE`, `DELETE`).
- When adding columns that reference another table (`customer_id` referencing `customers(id)`), gracefully handle column additions in existing SQLite databases by ignoring `OperationalError` when `ALTER TABLE ADD COLUMN` is called and the column already exists.
