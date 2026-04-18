# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.

## 2026-04-18 - Avoid Nested Links for Accessibility
**Learning:** Nesting interactive elements like `<a>` tags inside other `<a>` tags creates invalid HTML that breaks screen reader navigation, focus states, and automated testing locators like those used in Playwright.
**Action:** When designing lists where the entire item should be clickable but also contains separate actions (like a delete button), use a `<div>` or `<li>` wrapper with flexbox utilities (`d-flex justify-content-between`), and ensure each interactive action has its own distinct, un-nested `<a>` or `<button>` element.
