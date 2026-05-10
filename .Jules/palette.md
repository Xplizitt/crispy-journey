# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.

## 2025-05-15 - Invalid Nested Interactive Elements in List Groups
**Learning:** Found a pattern where `.list-group-item-action` classes were applied to an `<a>` tag to make the whole item clickable, but then a delete `<button>` or `<a>` tag was nested inside it. This creates invalid HTML (interactive content cannot be a descendant of another interactive element) and causes severe accessibility issues for screen reader users and confusing click targets.
**Action:** Replace the parent `<a>` wrapper with a standard `<div>` (e.g., `<div class="list-group-item d-flex...">`) and make only the specific text/content inside it the clickable link, while keeping the action buttons separate siblings.
