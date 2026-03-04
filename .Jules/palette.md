# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.

## 2024-05-24 - Fix nested interactive elements in edit part attachments list
**Learning:** Found nested interactive elements (`<a>` inside `<a>`) used for list items with delete buttons in `part_lister/templates/edit_part.html`. This breaks HTML validation and causes severe accessibility issues for screen readers. It's a critical pattern to avoid in the application's UI.
**Action:** Replaced the outer `<a>` tag with a `<div>` and kept the file link as an inner `<a>` tag, alongside the delete button which also received an `aria-label="Delete attachment"`.
