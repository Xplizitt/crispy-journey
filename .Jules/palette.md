# Palette UX Learnings

## 2026-03-11 - Add ARIA Labels to Icon-Only Buttons
**Learning:** Found multiple instances where Bootstrap icons (e.g., `<i class="bi bi-trash"></i>`) were used as standalone buttons or links for destructive actions without text content. Screen readers would not be able to announce the purpose of these buttons.
**Action:** Always verify that buttons or anchor tags containing only icons include descriptive `aria-label` and `title` attributes.

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.
