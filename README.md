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
