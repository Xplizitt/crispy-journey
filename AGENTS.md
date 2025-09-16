# Instructions for AI Agents

This document provides critical instructions for any AI agent working on this codebase. Please read and adhere to these guidelines at all times.

## 1. Changelog Maintenance (`agent_log.md`)

**This is the most important rule.**

For **every change** you make to the codebase, you **must** document it in the `agent_log.md` file. This includes, but is not limited to:
-   Creating, deleting, or modifying files.
-   Installing dependencies.
-   Running one-time scripts.
-   Any other action that affects the state of the repository.

Your log entry should be made **as soon as you complete the action**. Do not wait until the end of your session to update the log.

Each log entry must include:
-   **The Change:** A clear and concise description of what you did.
-   **The Reasoning:** A detailed explanation of *why* you made the change. This is crucial for project continuity.

If you make a change and then revert it, you must log both the change and the reversion, along with the reasoning for each.

## 2. Source File Header Comments

For major, architectural, or widespread changes, you should also add a note to the header comment of the affected source file(s).

-   **"Mile Markers":** These comments are intended to be "mile markers" that provide a high-level overview of the file's evolution, rather than the "inch markers" of the `agent_log.md`.
-   **When to Add:** Use your judgment. A good rule of thumb is to add a header comment if you are adding a new feature, refactoring a significant portion of the file, or making a change that affects the file's core purpose.
-   **Format:** The format is flexible, but it should be a brief, dated note. For example: `2025-09-16: Refactored to use the new authentication service.`

## 3. Environment Setup

To set up the development environment, you must run the following commands in order:

1.  **Install Python Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Install Playwright System Dependencies:**
    ```bash
    playwright install-deps
    ```

3.  **Install Playwright Browsers:**
    ```bash
    playwright install
    ```

## 4. Running Tests

To run the test suite, you must first ensure the database is initialized and the application is running.

1.  **Initialize the database:**
    ```bash
    python part_lister/database.py
    ```

2.  **Run the application in the background:**
    ```bash
    python part_lister/app.py &
    ```

3.  **Run the tests:**
    ```bash
    PYTHONPATH=. python -m pytest
    ```
