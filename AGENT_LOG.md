# Agent Log

This log file tracks changes made to the codebase by the AI agent. It includes the reasoning and thought process behind each change to provide context for future development and maintenance.

---

### 2025-09-16: Initial Log Setup

**Change:** Created the `AGENT_LOG.md` file.

**Reasoning:** The purpose of this file is to maintain a running log of all changes made to the codebase. This will help with project continuity and provide a clear record of the agent's actions and decision-making process. The initial entry explains the file's purpose.

---

### 2026-03-01: Added Category, Location, Stock, and Audit Trail

**Change:** Added new columns (`category`, `location`, `stock_quantity`, `reorder_level`) to the `parts` table and created a new `audit_log` table. Updated `app.py` and UI templates to handle these fields, enforce input validation on numeric inputs, and highlight low stock items in the admin table.
**Reasoning:** To expand the platform with industry-standard features (categories/tags, location/bin tracking, low stock alerts, audit trail history, and enhanced search filtering).
**Note:** Included `init_db_migrations` in `database.py` to seamlessly execute `ALTER TABLE` and `CREATE TABLE IF NOT EXISTS` commands so existing databases are safely upgraded upon running the app without wiping data.

---

### 2025-09-16: Debugging Database Initialization

**Change:** Temporarily modified `part_lister/database.py` to robustly locate the project root and print debugging information.

**Reasoning:** While working on the initial setup, the test suite was failing because it could not find the `parts.db` file. The original path logic in `database.py` was ambiguous and depended on the current working directory. To resolve this, I modified the script to find the project root by searching for the `.gitignore` file, ensuring the database was always created in the correct location. This change was necessary to get the tests to pass and verify the environment.

**Reversion:** After confirming that the tests passed, I reverted the changes to `part_lister/database.py`. This was done to keep the initial commit focused on the user's primary request, which was the creation of the `AGENT_LOG.md` file. The improvements to `database.py`, while useful, were considered out of scope for the initial task.

### 2025-09-16: Architectural Refactoring using Flask Blueprints

**Change:** Refactored `app.py` to use Flask Blueprints to separate concerns. Created `part_lister/routes` directory containing three new modules: `admin.py`, `scanner.py`, and `core.py`.
- Moved `/admin`, `/login`, `/logout`, `/add_part`, `/edit_part`, `/part`, `/gallery`, file handling, export/import routes to `admin_bp`.
- Moved `/scanner` route to `scanner_bp` to isolate legacy device endpoints.
- Moved `/`, `/add_to_list`, `/create_list`, `/switch_list`, API routes, edit/delete list items and `/print` routes to `core_bp`.
- Refactored `app.py` to register blueprints and serve as the main application factory. To satisfy the strict constraint of zero feature changes (particularly regarding HTML templates), a template context processor was introduced in `app.py` to transparently map original endpoint names in existing `url_for` calls to their new blueprint-prefixed names. Added Mile Marker comments to new route files and `app.py`.

**Reasoning:** To stabilize the codebase and separate logically distinct domains (Admin, Scanner, Core lists) into their own modules prior to adding new inventory tracking features. This keeps `app.py` streamlined and improves maintainability while preserving absolute backward compatibility with existing templates and legacy endpoints.
## 2024-xx-xx - Implemented Manufacturing BOM & Material Yield Tracking
**Modifications:**
*   `part_lister/database.py`: Added `part_type` column to `parts` table and created a new `bom_components` table to track parent/child relationship and required quantities.
*   `part_lister/routes/admin.py`:
    *   Updated `add_part` and `edit_part` to include the `part_type` field.
    *   Added endpoints `add_bom_component` and `remove_bom_component` for managing BOMs.
    *   Added the `build_part` endpoint, which calculates child components based on build quantity, deducts component stock, increments the parent's stock, and logs the actions to `audit_log`.
*   `part_lister/templates/edit_part.html`: Added a selector for `part_type` and a conditional UI for managing a part's BOM when the part type is set to Manufactured or Assembly.
*   `part_lister/templates/part_view.html`: Displays the `part_type`, BOM, and an interface to run the Build Action.
*   `part_lister/templates/admin.html`: Added the `Type` column.

**Architectural Reasoning:**
The BOM structure is a many-to-many relationship using a junction table (`bom_components`), but we model it specifically with a `quantity_required` field in order to define precisely the amount to consume when building the parent component. Real numbers are used for quantities so that fractional consumption is allowed. The database migration logic uses `PRAGMA table_info` and checks for column existence before adding it to avoid catastrophic deletion. Pre-commit commands complete verifying changes.
