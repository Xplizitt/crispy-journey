# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.

## 2026-06-19 - Adding ARIA labels to Icon-Only Buttons and Fixing Nested Links
**Learning:** Icon-only buttons using Bootstrap Icons (`<i class="bi bi-*"></i>`) within forms, tables, and list groups lack implicit text descriptions, making them inaccessible to screen readers unless explicitly labeled. Furthermore, nesting interactive elements like a delete `<button>` or `<a>` inside a parent `<a>` tag creates invalid HTML that breaks accessibility trees and E2E test locators.
**Action:** Always add descriptive `aria-label` and `title` attributes to icon-only interactive elements. When building list items with both a primary link and secondary actions, use a block container (like a `<div>`) with flexbox utilities (`d-flex justify-content-between`), and ensure no interactive elements are nested within one another.
