# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.

## 2026-03-08 - Nested Interactive Elements Break Accessibility
**Learning:** Placing an interactive element (like a delete `<button>` or `<a>`) inside another interactive element (like an `<a>` tag used as a list item container) is invalid HTML and severely breaks screen reader navigation, as the accessibility tree cannot determine which element receives focus or interaction.
**Action:** Always use neutral container tags like `<div>` or `<li>` when nesting interactive elements, such as a clickable link alongside an icon-only delete button, and remember to include ARIA labels on the icon-only buttons.
