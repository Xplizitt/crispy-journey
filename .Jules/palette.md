# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.

## 2026-04-05 - Empty States in Dynamic Lists
**Learning:** When adding empty states to dynamic lists that use client-side polling, the visual empty state component in the Jinja2 HTML template can be completely overwritten and revert to the old state if the client-side JavaScript rendering logic isn't identically updated.
**Action:** Always verify client-side rendering functions (like `renderListTable` in `app.js`) when changing default/initial DOM states in Jinja2 templates for dynamically updated sections.
