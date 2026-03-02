from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto("http://127.0.0.1:5000/login")
        page.get_by_placeholder("Password").fill("admin")
        page.get_by_role("button", name="Login").click()
        page.wait_for_load_state("networkidle")
        page.goto("http://127.0.0.1:5000/admin")
        page.get_by_role("button", name="Import Parts").click()
        page.screenshot(path="screenshot_admin_test.png", full_page=True)
        browser.close()

run()
