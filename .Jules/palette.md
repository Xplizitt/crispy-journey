# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.
## 2025-05-23 - Avoid nested `<a>` tags in list-group-items
**Learning:** List-group-items in this app sometimes use an `<a>` tag as the outer container while nesting other interactive elements (like delete buttons) inside. This creates invalid HTML that breaks screen reader accessibility and Playwright locators.
**Action:** Replace the outer `<a>` tag with a `<div>` and make the text/content inside an `<a>` link instead.
