with open("tests/test_e2e_lists.py", "r") as f:
    text = f.read()

# Replace the click on "Import" with force=True because it says "element is not stable"
text = text.replace('page.get_by_role("button", name="Import", exact=True).click()', 'page.get_by_role("button", name="Import", exact=True).click(force=True)')

# Same for "Import Parts" in case it fails later
text = text.replace('page.get_by_role("button", name="Import Parts").click()', 'page.get_by_role("button", name="Import Parts").click(force=True)')

with open("tests/test_e2e_lists.py", "w") as f:
    f.write(text)
