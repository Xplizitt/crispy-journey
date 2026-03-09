# Test Framework Review — 5 Improvements

## Current State

The project has **4 tests across 3 files** covering a multi-blueprint Flask application with 5 route modules and dozens of endpoints:

| File | Tests | What's Covered |
|---|---|---|
| `test_app.py` | 1 | Index page smoke test |
| `test_customers.py` | 2 | Customer create + view |
| `test_e2e_lists.py` | 1 | List workflow (E2E via Playwright) |

No `conftest.py`, no `pytest.ini`/`pyproject.toml`, no coverage tooling, no test markers.

---

## Improvement 1: Add a shared `conftest.py` with reusable fixtures

**Problem:** Each test file defines its own `client` fixture with inconsistent isolation. `test_app.py` uses the production database (no isolation), while `test_customers.py` uses `tmp_path` correctly. Fixture logic is duplicated and divergent.

**Solution:** Create `tests/conftest.py` with a single, properly-isolated `client` fixture:
- Uses `tmp_path_factory` (session-scoped) or `tmp_path` (function-scoped) for a temp SQLite database
- Initializes the schema via `init_db()`
- Sets `TESTING=True` in Flask config
- Provides an `auth_client` variant that pre-sets `session['logged_in'] = True`

This eliminates duplication and ensures every test runs against an isolated database.

---

## Improvement 2: Add pytest configuration and code coverage

**Problem:** No pytest configuration exists anywhere (no `pytest.ini`, `pyproject.toml`, or `setup.cfg`). `pytest-cov` is not installed, so there's no visibility into what code is or isn't tested.

**Solution:**
1. Add `pytest-cov` to `requirements.txt`
2. Create `pyproject.toml` with:
   ```toml
   [tool.pytest.ini_options]
   testpaths = ["tests"]
   markers = [
       "e2e: end-to-end tests requiring a running server",
       "unit: fast unit/integration tests",
   ]

   [tool.coverage.run]
   source = ["part_lister"]

   [tool.coverage.report]
   show_missing = true
   fail_under = 50
   ```
3. Run with `pytest --cov=part_lister tests/` to see coverage reports.

---

## Improvement 3: Expand route test coverage

**Problem:** 4 out of 5 blueprints are untested or barely tested at the unit level:

| Blueprint | Unit Tests | Status |
|---|---|---|
| `core_bp` | 0 | Only E2E coverage |
| `admin_bp` | 0 | Completely untested |
| `work_orders_bp` | 0 | Completely untested |
| `scanner_bp` | 0 | Completely untested |
| `customers_bp` | 2 | Partially covered |

**Solution:** Add test modules for each untested blueprint:
- `test_admin.py` — login/logout, parts CRUD, import/export, gallery upload
- `test_work_orders.py` — work order and task lifecycle
- `test_scanner.py` — scanner page loads, basic form submissions
- `test_core.py` — list CRUD, add/remove items, print view, `/api/lists/<id>/items`

Priority: `admin_bp` and `core_bp` first, as they contain the most critical business logic.

---

## Improvement 4: Fix fragile E2E test infrastructure

**Problem:** `run_e2e.py` has multiple reliability issues:
- `time.sleep(3)` is a race condition — the server may not be ready (slow machines) or the wait is wasted (fast machines)
- Tests use the **production database**, not an isolated one
- `os.system('python part_lister/database.py')` reinitializes the real DB
- Hardcoded `http://127.0.0.1:5000` ignores the installed `pytest-base-url` plugin
- `os.remove('part_to_add.csv')` cleanup won't run if the test fails mid-execution

**Solution:**
1. Replace `sleep(3)` with a health-check polling loop (retry `GET /` until 200 or timeout after 10s)
2. Start the server with `DATABASE_PATH` pointing to a temp directory
3. Use a session-scoped pytest fixture in `conftest.py` to manage server lifecycle
4. Use `pytest-base-url` or a fixture for the server URL
5. Use `tmp_path` for the CSV file so cleanup is automatic regardless of test outcome

---

## Improvement 5: Add test markers to separate unit and E2E tests

**Problem:** Unit tests and E2E tests are co-mingled in `tests/` with no way to run them selectively. Running `pytest tests/` attempts E2E tests (which fail without a running server) alongside unit tests. This makes fast local iteration impossible and complicates CI setup.

**Solution:**
1. Register markers in pytest config (see Improvement 2)
2. Apply `@pytest.mark.e2e` to `test_e2e_lists.py`
3. Apply `@pytest.mark.unit` to unit test files (optional, as non-E2E is the default)
4. Usage:
   - `pytest -m "not e2e"` — fast local iteration (unit tests only)
   - `pytest -m e2e` — E2E tests only (requires server)
   - `pytest` — everything
5. In CI, run unit tests on every push and E2E tests on merge/schedule
