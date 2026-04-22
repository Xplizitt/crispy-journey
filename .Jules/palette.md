# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.
## 2024-04-22 - Nested Interactive Elements in Jinja2
**Learning:** Found nested `<a>` tags (an interactive button nested inside a parent link) in the Jinja2 template (`edit_part.html`), which creates invalid HTML and severely degrades accessibility because screen readers and assistive technologies cannot properly parse or interact with nested links.
**Action:** Always replace parent link wrappers containing interactive sub-elements (like "Delete" buttons) with non-interactive container elements like `<div>` or `<li>`, styling them appropriately (e.g. `list-group-item d-flex justify-content-between align-items-center`) and making the discrete actions into separate, sibling links/buttons.
