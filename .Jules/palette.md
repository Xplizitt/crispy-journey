# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.

## 2026-07-04 - Fix invalid nested anchor tags and add missing ARIA labels
**Learning:** Found instances where a `list-group-item-action` link tag directly wrapped another `<a class="btn ...">` icon-only action button in Jinja2 templates (e.g. `edit_part.html`). This is invalid HTML that can break browser rendering and screen reader accessibility, and also cause failures with UI automation frameworks like Playwright.
**Action:** When creating list items with inline actions, use a `<div>` or `<li>` for the main structural container instead of a wrapper `<a>`. Apply text links to the inner text explicitly while keeping the action buttons separate, ensuring clean HTML syntax and functional separation.
