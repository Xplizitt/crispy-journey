# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.

## 2024-04-15 - Avoid Nested Interactive Elements
**Learning:** Nesting interactive elements, such as placing a button or a secondary `<a>` tag (like a delete action) inside a parent `<a>` tag, breaks screen reader accessibility and results in invalid HTML. Screen readers struggle to announce and navigate such structures correctly, and browser behavior can be unpredictable.
**Action:** Always separate discrete UI actions into sibling elements within a non-interactive container (like a `<div>` or `<li>`). For example, instead of wrapping an entire list item row in a link, use a `<div>` container with the primary text as one link and the secondary action (like a delete button) as a separate element alongside it.
