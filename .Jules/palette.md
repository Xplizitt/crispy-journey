# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.
## 2025-10-24 - Avoiding nested interactive elements in list groups
**Learning:** Placing interactive elements (like a delete button) inside an anchor tag that acts as a container for a list item creates invalid HTML. Screen readers struggle with nested interactive elements, and it can cause unreliable behavior for automated tests (like Playwright locators).
**Action:** Replace outer anchor tags with `<div>` containers when multiple distinct interactive actions (e.g., viewing a file and deleting it) exist within the same list item, separating the actions into their own distinct tags.
