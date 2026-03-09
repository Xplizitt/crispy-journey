import os
import pytest

playwright = pytest.importorskip("playwright")
from playwright.sync_api import Page, expect

BASE_URL = "http://127.0.0.1:5000"


@pytest.mark.e2e
def test_multiple_list_workflow(page: Page, tmp_path):
    """
    Tests the full user workflow for creating, switching, and managing multiple lists.
    """
    # --- 1. DB Setup & Add Part to DB ---
    csv_file = tmp_path / "part_to_add.csv"
    csv_file.write_text(
        'Barcode,Description,Part Number,UOM,Supplier Name\n'
        'E2E-TEST-001,E2E Test Part,E2E-01,Each,E2E Supplier\n'
    )

    # Login
    page.goto(f"{BASE_URL}/login")
    page.get_by_placeholder("Password").fill("admin")
    page.get_by_role("button", name="Login").click()
    expect(page.get_by_text("You were logged in")).to_be_visible()

    # Import the part
    page.goto(f"{BASE_URL}/admin")
    page.get_by_role("link", name="Import Parts").click()
    page.locator("input[name='file']").set_input_files(str(csv_file))
    page.get_by_role("button", name="Import", exact=True).click()
    expect(page.get_by_text("Successfully imported 1 parts.")).to_be_visible()

    # --- 2. Verify Default List and Add Item ---
    page.goto(f"{BASE_URL}/")
    expect(page.get_by_role("button", name="Current List: Default List")).to_be_visible()

    # Add item via AJAX
    page.get_by_placeholder("Barcode").fill("E2E-TEST-001")
    page.get_by_role("button", name="Add Item").click()
    expect(page.locator("tr", has_text="E2E-TEST-001")).to_be_visible()

    # --- 3. Create a New List ---
    page.get_by_role("button", name="Current List: Default List").click()
    page.get_by_role("link", name="Create New List...").click()
    page.get_by_placeholder("New list name...").fill("E2E Test List")
    page.get_by_role("button", name="Create").click()

    # --- 4. Verify New List is Active and Empty ---
    expect(page.get_by_text("List 'E2E Test List' created successfully.")).to_be_visible()
    expect(page.get_by_role("button", name="Current List: E2E Test List")).to_be_visible()
    expect(page.get_by_text("No items in list.")).to_be_visible()

    # --- 5. Switch Back to Default List ---
    page.get_by_role("button", name="Current List: E2E Test List").click()
    page.get_by_role("link", name="Default List").click()

    # --- 6. Verify Original Item is Present ---
    expect(page.get_by_role("button", name="Current List: Default List")).to_be_visible()
    expect(page.locator("tr", has_text="E2E-TEST-001")).to_be_visible()
