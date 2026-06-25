# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.

## 2026-06-25 - Structured Empty States
**Learning:** Replacing plain text empty states (like "No items found") with a structured empty state component (featuring an icon, clear title, and instructional text) significantly improves usability. It provides visual feedback that a list is intentionally empty, rather than appearing as a broken or unstyled table row, and guides the user on how to populate the data.
**Action:** When creating or modifying tables that can be empty, always implement a structured empty state. Ensure both server-rendered templates (Jinja2 `{% else %}`) and client-side rendering (`app.js`) produce identical, styled empty state markup.
