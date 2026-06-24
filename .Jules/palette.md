# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.

## 2024-06-24 - Avoid Nested Interactive Elements in Jinja2
**Learning:** In Jinja2 HTML templates, avoid nesting `<a>` tags or other interactive elements (like buttons) inside parent `<a>` tags. This creates invalid HTML that breaks screen reader accessibility and Playwright locators.
**Action:** Replace the outer `<a>` with a `<div>` or appropriate block element, and style it appropriately.
