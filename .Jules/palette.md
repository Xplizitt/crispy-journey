# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.
## 2026-06-18 - Add structured empty states to lists
**Learning:** When rendering data tables with Jinja2 loops (e.g., `{% for part in parts %}`), the table can look broken or confusing if it's completely empty. Furthermore, hardcoded E2E test assertions can break when text is updated.
**Action:** Always include an `{% else %}` block to render a structured empty state with an icon and helpful text when the database is empty or searches yield no results. Also, ensure corresponding E2E tests are updated to assert the new text.
