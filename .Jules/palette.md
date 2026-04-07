# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.
## 2024-04-07 - Add ARIA Labels to Icon-Only Buttons
**Learning:** Icon-only buttons (like delete trash cans, edit pencils, and navigation arrows) in this application's tables and modals frequently lacked `aria-label` attributes, making them inaccessible to screen readers.
**Action:** When adding or modifying icon-only buttons or links, always include an `aria-label` (and optionally a `title`) attribute to ensure screen reader compatibility.
