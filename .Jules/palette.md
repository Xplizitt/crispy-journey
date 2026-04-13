# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.

## 2024-04-13 - Nested Interactive Elements inside Anchor Tags
**Learning:** Placing interactive elements (like a delete button or link) inside an `<a>` tag results in invalid HTML and severely breaks screen reader parsing and keyboard navigation, causing unexpected behavior when interacting with the element.
**Action:** When creating list items that need to be clickable but also contain secondary actions (like delete), use a structural container (like `<div>` or `<li>`) and place the main link and secondary actions as siblings, using CSS to style the layout (e.g. Flexbox with `flex-grow-1`).
