# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.
## 2026-05-19 - Improved A11y for Delete and View Icon-only Buttons
**Learning:** Icon-only buttons (like the Bootstrap 'bi-trash' and 'bi-eye' icons) used in templates are completely invisible to screen readers without an `aria-label`. Additionally, we must never nest an interactive `<a>` element inside another `<a>` (e.g. an attachment link wrapping a delete button), as this violates HTML specifications and breaks a11y completely.
**Action:** When working on lists with multiple icon-based actions, ensure every icon-only `<a>` or `<button>` has `aria-label` and `title` attributes. If one interactive link is nested within another, convert the outer link to a container element like a `<div>` and update the styling appropriately to preserve layout.
