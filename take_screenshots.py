import sys
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Log in first
        page.goto("http://127.0.0.1:5000/login")
        page.fill("input[name='password']", "admin")
        page.click("button[type='submit']")

        # Create some data for screenshots
        import sqlite3
        conn = sqlite3.connect('parts.db')
        c = conn.cursor()

        # 1. Add a customer
        c.execute("INSERT INTO customers (name, email) VALUES ('Test Customer', 'test@example.com')")
        customer_id = c.lastrowid

        # 2. Add a part
        c.execute("INSERT INTO parts (barcode, part_number, description, stock_quantity) VALUES ('12345', 'PN-1', 'Test Part', 10)")
        part_id = c.lastrowid

        # 3. Add an attachment
        c.execute("INSERT INTO attachments (part_id, filename, filepath) VALUES (?, 'test.png', '/tmp/test.png')", (part_id,))
        attachment_id = c.lastrowid

        # 4. Add a work order
        c.execute("INSERT INTO work_orders (customer_id, title) VALUES (?, 'Test WO')", (customer_id,))
        wo_id = c.lastrowid

        # 5. Add a work order task with part
        c.execute("INSERT INTO work_order_tasks (work_order_id, description) VALUES (?, 'Test Task')", (wo_id,))
        task_id = c.lastrowid
        c.execute("INSERT INTO task_parts (task_id, part_id, quantity) VALUES (?, ?, 1)", (task_id, part_id))

        # 6. Add a work order log
        c.execute("INSERT INTO work_order_logs (work_order_id, description) VALUES (?, 'Test Log')", (wo_id,))

        conn.commit()
        conn.close()

        # Capture work order view
        page.goto(f"http://127.0.0.1:5000/work_orders/{wo_id}")
        page.screenshot(path="wo_view.png", full_page=True)

        # Capture part edit view
        page.goto(f"http://127.0.0.1:5000/edit_part/{part_id}")
        page.screenshot(path="part_edit.png", full_page=True)

        # Capture customer view
        page.goto(f"http://127.0.0.1:5000/customers/{customer_id}")
        page.screenshot(path="customer_view.png", full_page=True)

        browser.close()

if __name__ == "__main__":
    run()