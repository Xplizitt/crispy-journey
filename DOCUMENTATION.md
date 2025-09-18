# Part Lister Application Documentation

## 1. Overview

Welcome to the Part Lister application documentation. This document provides a comprehensive guide for both end-users and developers.

Part Lister is a web-based application designed for efficient management of parts and the creation of picking lists. It features two distinct user interfaces: a modern, feature-rich desktop interface and a lightweight, compatibility-focused interface for handheld barcode scanners running legacy operating systems like Windows CE 6.0.

## 2. For Users

### 2.1. Accessing the Application

*   **Main Interface**: `http://<your-server-ip>:5000/`
*   **Admin Panel**: `http://<your-server-ip>:5000/admin`
*   **Scanner Interface**: `http://<your-server-ip>:5000/scanner`

The default password for the admin panel is `admin`.

### 2.2. Core Concepts

*   **Parts**: Individual items in your inventory. Each part has a unique barcode, a description, and other optional details like part number, supplier, and notes.
*   **Assemblies**: A special type of part that is composed of other parts. For example, a "Wheel Assembly" part could be made up of one "Tire" part and one "Rim" part.
*   **Attachments**: Files (like images, PDFs, or CAD files) that can be associated with a part.
*   **Lists**: Collections of parts that you want to pick or assemble. You can create multiple lists (e.g., "Order 123", "Project X").

### 2.3. Using the Admin Panel (`/admin`)

The admin panel is the central hub for managing your parts database.

*   **Adding a Part**: Use the "Add New Part" form. A barcode and description are required. You can also upload attachments at the same time.
*   **Editing a Part**: Click the "Edit" button next to any part. From the edit screen, you can change part details, upload new attachments, delete existing attachments, and set a thumbnail image from one of the part's image attachments.
*   **Deleting a Part**: Click the "Delete" button. This will remove the part from the database. Its attachments will be kept in the system but will no longer be associated with that part.
*   **Bulk Actions**: Select multiple parts using the checkboxes and then choose an action from the "Bulk Actions" dropdown, such as "Delete" or "Set Thumbnail".
*   **Filtering and Exporting**: Use the filter fields at the top of the list to narrow down your view. You can then click "Export as CSV" to download the filtered list.
*   **Importing**: You can bulk-import parts from a CSV file. The file must have the columns: `Barcode`, `Description`, `Part Number`, `UOM`, `Supplier Name`.

### 2.4. Using the Main List-Building Interface (`/`)

This is the primary interface for building lists on a desktop computer.

*   **Switching Lists**: Use the dropdown menu to switch between lists or create a new one.
*   **Adding Items**: Use the form at the top to add items by barcode. The system uses AJAX, so the list updates automatically without a page reload.
*   **Viewing Assemblies**: Assemblies are shown in bold. You can click on them to expand and see their constituent parts.

### 2.5. Using the Scanner Interface (`/scanner`)

This interface is designed for speed and simplicity on handheld devices.

*   **Workflow**: The page is designed for a keyboard-wedge barcode scanner. The typical workflow is:
    1.  Scan a barcode. The scanner inputs the text and should be configured to press `Enter`.
    2.  The cursor automatically moves to the "Quantity" field.
    3.  Type the quantity.
    4.  Press `Enter` to submit the item. The page will reload.
*   **List Management**: You can switch between lists or create new ones using the controls at the top of the page.
*   **Editing/Deleting**: Basic links are provided to edit the quantity of an item or delete it from the list.

## 3. For Developers

### 3.1. Codebase Structure

```
part_lister/
├── app.py              # Main Flask application file (all routes and logic)
├── database.py         # Script to initialize the database schema
├── static/
│   ├── css/
│   │   ├── custom.css
│   │   └── dark_theme.css
│   └── js/
│       └── app.js      # JavaScript for the main/modern interface
└── templates/
    ├── admin.html
    ├── base.html
    ├── index.html      # Template for the main list-building interface
    ├── scanner.html    # Template for the simplified scanner interface
    └── ... (other templates)
```

### 3.2. Setting Up the Development Environment

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Initialize the Database**:
    This will create a `parts.db` file in the project root.
    ```bash
    python part_lister/database.py
    ```
3.  **Run the Application**:
    ```bash
    python part_lister/app.py
    ```
    The application will be running at `http://0.0.0.0:5000/`.

### 3.3. Key Architectural Considerations

*   **Monolithic Design**: The application is intentionally simple, with all backend logic in `app.py`. For larger applications, consider a more structured approach (e.g., using Flask Blueprints).
*   **Two Frontends**: Be mindful of the two distinct user interfaces. Changes to the main UI should not affect the scanner UI.
    *   **Main UI**: Uses modern tools (Bootstrap 5, `fetch` API). Feel free to use modern web features here.
    *   **Scanner UI**: Must remain highly compatible. Use basic HTML, simple CSS, and vanilla ES3-compliant JavaScript. Avoid external libraries.
*   **Database Migrations**: There is no database migration system (like Alembic). To change the schema, you must edit `database.py` and re-initialize the database, which will wipe all data. This is only suitable for development.

### 3.4. Running Tests

The project uses `pytest`.

1.  Make sure the application is running in the background:
    ```bash
    python part_lister/app.py &
    ```
2.  Run the tests from the project root:
    ```bash
    PYTHONPATH=. python -m pytest
    ```
