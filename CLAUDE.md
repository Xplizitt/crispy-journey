# CLAUDE.md

## Project Overview

Part Lister — a Flask/SQLite web application for managing parts inventory and creating pick lists. Features two UIs: a modern Bootstrap 5 interface and a legacy Windows CE 6.0-compatible scanner interface for handheld barcode scanners.

## Tech Stack

- **Backend:** Python 3, Flask 3.1, SQLite3
- **Frontend:** Bootstrap 5.3 (CDN), Jinja2 templates, vanilla ES6+ JavaScript
- **Testing:** Pytest, Playwright (E2E)
- **Image processing:** Pillow

## Setup & Running

```bash
pip install -r requirements.txt
python part_lister/database.py        # Initialize/migrate the database
PYTHONPATH=. python part_lister/app.py  # Start server on localhost:5000
```

## Testing

```bash
pytest tests/                  # Unit tests
python run_e2e.py              # E2E tests (Playwright)
```

Test files: `tests/test_app.py` (Flask fixture), `tests/test_e2e_lists.py` (list workflows), `tests/test_customers.py` (customer CRUD). Tests use temporary SQLite databases for isolation.

## Project Structure

```
part_lister/
├── app.py              # Flask app init, blueprint registration, config
├── database.py         # Schema definition, migrations, get_db()
├── routes/
│   ├── admin.py        # Admin: parts CRUD, gallery, import/export, bulk edit
│   ├── core.py         # Lists: create, switch, add/remove items, print
│   ├── scanner.py      # Legacy scanner interface
│   ├── customers.py    # Customer CRUD
│   └── work_orders.py  # Work orders & tasks management
├── templates/           # Jinja2 templates (base.html, index.html, admin.html, etc.)
├── static/
│   ├── css/            # custom.css, dark_theme.css
│   ├── js/app.js       # AJAX, theme toggling, polling, keyboard handling
│   ├── uploads/        # User-uploaded files
│   └── thumbnails/     # Generated 128x128 thumbnails
tests/                   # Pytest + Playwright tests
```

## Architecture

### Blueprints

Five Flask blueprints, each in `part_lister/routes/`:
- `admin_bp` — `/login`, `/admin`, `/add_part`, `/edit_part/<id>`, `/delete_part/<id>`, `/export_parts`, `/import_parts`, `/gallery`
- `core_bp` — `/`, `/add_to_list`, `/create_list`, `/switch_list/<id>`, `/print/<id>`, `/api/lists/<id>/items`
- `scanner_bp` — `/scanner`
- `customers_bp` — `/customers/`
- `work_orders_bp` — `/work_orders/`

### Database

SQLite with key tables: `parts`, `lists`, `list_items`, `customers`, `work_orders`, `work_order_tasks`, `task_parts`, `attachments`, `bom_components`, `audit_log`.

**Migrations:** `init_db_migrations()` in `database.py` adds columns gracefully using try-catch around `ALTER TABLE` to handle already-existing columns.

### Authentication

Simple session-based login using `ADMIN_PASSWORD` env var (default: `admin`). Protects `/admin`, `/customers/`, and `/work_orders/` routes.

## Code Conventions

- **Database access:** Use `get_db()` to get a connection. Each blueprint defines its own `get_db()` to avoid circular imports.
- **Writes require commit:** Always call `db.commit()` after INSERT/UPDATE/DELETE operations.
- **Templates:** Use `url_for('blueprint.endpoint')` for URLs. A context processor maps old function names to blueprint endpoints for backward compatibility.
- **File uploads:** Validate against `ALLOWED_EXTENSIONS` whitelist. Use `secure_filename()`. Thumbnails are 128x128 PNGs generated via Pillow.
- **User feedback:** Use `flash()` messages for success/error notifications.
- **Form handling:** Routes support both JSON (`request.json`) and form-urlencoded (`request.form`) POST data.
- **Error handling:** Try-catch for SQLite operations; graceful column addition in migrations.

## Frontend Conventions

- **Accessibility:** Icon-only buttons must include `aria-label` attributes. Images need alt text.
- **Scanner page (`/scanner`):** Must remain compatible with Internet Explorer on Windows CE 6.0. No modern JavaScript (no fetch, arrow functions, template literals, etc.).
- **Theme:** Dark/light toggle stored in LocalStorage. Styles in `dark_theme.css`.
- **Polling:** Main interface auto-polls every 5 seconds for list updates.
- **Bootstrap:** Use `align-middle` on table cells, `shadow-sm` for container depth.

## Environment Variables

| Variable | Purpose | Default |
|---|---|---|
| `ADMIN_PASSWORD` | Password for admin login | `admin` |
| `PYTHONPATH` | Set to `.` for running the app | — |

## Important Gotchas

1. **Each blueprint has its own `get_db()`** — don't try to import it from another blueprint or a shared module.
2. **Scanner page must stay IE-compatible** — no ES6+ features, no fetch API, no modern CSS. Test changes in basic HTML.
3. **SQLite migrations are additive** — columns are added via try-catch `ALTER TABLE` in `init_db_migrations()`. Never drop and recreate tables.
4. **`db.commit()` is mandatory** — SQLite won't persist changes without an explicit commit after writes.
5. **Uploads directory** — `part_lister/static/uploads/` and `thumbnails/` are not tracked in git but must exist at runtime.
