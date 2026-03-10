# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.

## 2025-03-10 - Add ARIA Labels to Delete Icon-Only Buttons
**Learning:** Icon-only buttons without `aria-label` or `title` attributes are completely opaque to screen readers, making destructive actions like deleting tasks and logs inaccessible.
**Action:** Always ensure that any `<button>` or `<a>` tag that relies solely on an icon (e.g., `<i class="bi bi-trash"></i>`) includes descriptive `aria-label` and `title` attributes (e.g., `aria-label="Delete" title="Delete"`).
