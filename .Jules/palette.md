# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.

## 2026-04-02 - Fix Nested Anchor Tags in Edit Part View
**Learning:** Nesting interactive elements like `<a>` tags within other `<a>` tags creates invalid HTML, breaking screen reader context and keyboard navigation patterns for users.
**Action:** Always use container elements like `<div>` with appropriate utility classes to group interactive elements side-by-side instead of nesting them.
