# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## 2025-09-16 - Avoid nested interactive elements
**Learning:** Nesting interactive elements (like an `<a>` tag for a delete button inside another `<a>` tag serving as a list item container) creates invalid HTML, breaking screen reader navigation, keyboard accessibility, and automated locators (like Playwright).
**Action:** Use a non-interactive container (like `<div>` or `<li>`) for the list item and place the interactive elements (links, buttons) separately inside it.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.
