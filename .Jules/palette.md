# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.
## 2026-05-12 - Nested Interactive Elements inside Anchor Tags
**Learning:** Avoid nesting interactive elements (like `<a>` tags or buttons) inside parent `<a>` tags in HTML templates (e.g., when building list items). This creates invalid HTML, breaks screen reader accessibility, and causes unpredictable click behavior in browsers.
**Action:** Always use neutral container tags like `<div>` or `<li>` to wrap sibling interactive elements (e.g., a file link next to a delete button) and apply Flexbox classes to position them correctly.
