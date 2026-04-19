# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.

## 2024-05-16 - Empty States During Polling
**Learning:** When adding or updating visual empty states in Jinja templates for tables that are also updated via client-side JavaScript polling (like `renderListTable` in `app.js`), the exact same HTML markup must be duplicated in the JS function. Otherwise, the empty state will "flash" between the nicely styled Jinja version and the unstyled JS version every time the polling triggers.
**Action:** Always check for corresponding JavaScript render functions when modifying initial DOM states in templates that use background polling for updates.
