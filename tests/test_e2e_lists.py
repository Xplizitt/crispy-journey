import os
from playwright.sync_api import Page, expect

def test_multiple_list_workflow(page: Page):
    """
    Tests the full user workflow for creating, switching, and managing multiple lists.
    """
    # --- 1. DB Setup & Add Part to DB ---
    # It's better to do this setup via API calls or DB fixtures in a real test suite,
    # but for this task, using the UI to set up state is acceptable.
    os.system('python part_lister/database.py')
    with open('part_to_add.csv', 'w') as f:
        f.write('Barcode,Description,Part Number,UOM,Supplier Name\n')
        f.write('E2E-TEST-001,E2E Test Part,E2E-01,Each,E2E Supplier\n')

    # Login
    page.goto("http://127.0.0.1:5000/login")
    page.get_by_placeholder("Password").fill("admin")
    page.get_by_role("button", name="Login").click()
    expect(page.get_by_text("You were logged in")).to_be_visible()

    # Import the part
    page.goto("http://127.0.0.1:5000/admin")
    page.get_by_role("link", name="Import Parts").click()
    page.locator("input[name='file']").set_input_files('part_to_add.csv')
    page.get_by_role("button", name="Import", exact=True).click()
    expect(page.get_by_text("Successfully imported 1 parts.")).to_be_visible()

    # --- 2. Verify Default List and Add Item ---
    page.goto("http://127.0.0.1:5000/")
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

    # Clean up the test file
    os.remove('part_to_add.csv')
