# Palette UX Learnings

## 2026-04-09 - Icon-Only Buttons Accessibility
**Learning:** Icon-only action buttons (e.g., trash can icons for deleting items in attachment lists or nested components like work order logs) often lack text content. While they look intuitive visually, they are completely opaque to screen readers without proper aria-labels. Adding `aria-label` and `title` attributes improves both screen reader accessibility and provides tooltip hints for visual users.
**Action:** When adding or maintaining icon-only buttons (`<a>` or `<button>`), especially in repeating structures like lists or tables, ALWAYS ensure they have descriptive `aria-label` and `title` attributes.

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.
