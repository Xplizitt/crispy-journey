# Part Lister Web Application

A simple web application for building part lists, designed with a /scanner page to be compatible with handheld scanners running Windows CE 6.0.

## Technology Stack

*   **Backend:** Python 3 with Flask
*   **Database:** SQLite 3

## Features

*   **Part Management:** A password-protected admin page to add, edit, and delete parts from the database.
*   **List Building:** A simple interface for scanning barcodes and adding items to a list.
*   **Print View:** A print-optimized view of the current parts list.
*   **Error Handling:** Displays messages for invalid barcodes.
*   **Scanner Friendly:** The main page and scanner page auto-focuses the barcode input field for use with keyboard-wedge scanners.
*   **Old Scanner Compat:** The /scanner page remains a compatible frontend for Windows CE 6.0 scanners using Internet Explorer

## Setup and Running

1.  **Clone the repository.**
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    If you intend to run the Playwright tests, you will also need to install the Playwright system dependencies and browsers:
    ```bash
    playwright install-deps
    playwright install
    ```
3.  **Initialize the database:**
    ```bash
    python part_lister/database.py
    ```
4.  **Run the application:**
    ```bash
    PYTHONPATH=. python part_lister/app.py
    ```
5.  **Access the application:**
    Open a web browser and navigate to `http://localhost:5000`.
    *   **Main Interface:** `http://localhost:5000/`
    *   **Admin Interface:** `http://localhost:5000/admin` (Password protected)
    *   **Scanner Interface:** `http://localhost:5000/scanner`

## Environment Variables

*   **`ADMIN_PASSWORD`**: Required for accessing the admin interface (`/admin`). Set this variable in your environment before running the application.
*   **Default Password:** If the `ADMIN_PASSWORD` environment variable is not set, the default password is `admin`.
