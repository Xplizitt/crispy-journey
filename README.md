# Part Lister Web Application

A simple web application for building part lists, designed to be compatible with handheld scanners running Windows CE 6.0.

## Technology Stack

*   **Backend:** Python 3 with Flask
*   **Database:** SQLite 3

## Features

*   **Part Management:** A password-protected admin page to add, edit, and delete parts from the database.
*   **List Building:** A simple interface for scanning barcodes and adding items to a list.
*   **Print View:** A print-optimized view of the current parts list.
*   **Error Handling:** Displays messages for invalid barcodes.
*   **Scanner Friendly:** The main page auto-focuses the barcode input field for use with keyboard-wedge scanners.

## Setup

1.  **Install Dependencies:**
    ```bash
    pip install Flask
    ```

2.  **Initialize the Database:**

    This will create a `parts.db` file in the root directory.
    ```bash
    python part_lister/database.py
    ```

## Running the Application

To run the development server:

```bash
python part_lister/app.py
```

The application will be available at `http://0.0.0.0:5000/`.

*   **Main Page:** `http://<your-ip>:5000/`
*   **Admin Page:** `http://<your-ip>:5000/admin` (Password is `admin`)

## How to Use

### Admin
1.  Go to the `/admin` page and log in with the password.
2.  Use the form to add new parts to the database.
3.  Edit or delete existing parts from the table.

### Main Page (Scanner)
1.  Navigate to the main page. The cursor will be in the "Barcode" field.
2.  Scan a barcode. The scanner should input the barcode and press "Tab".
3.  The cursor will move to the "Quantity" field. Type the quantity.
4.  The scanner should be configured to press "Enter" after the quantity, which will submit the form.
5.  The page will reload with the new item in the list.
6.  When the list is complete, click "Print List" to open the print view.
