# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.

## 2026-05-24 - Avoid Nested Links for Interactive List Items
**Learning:** Nesting `<a>` tags (e.g., placing a delete button link inside an `<a>` that wraps a file name) creates invalid HTML, completely breaking screen reader accessibility and making Playwright locators fail.
**Action:** Always separate interactive targets within list items (like using a flex container `<div>`) and give each action its own explicit link or button with an appropriate `aria-label`.
