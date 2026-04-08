# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.

## 2024-05-14 - Fix Nested Links in Bootstrap List Groups
**Learning:** Using an `<a>` tag as a `.list-group-item` container in Bootstrap is common for entire rows that are clickable. However, when placing secondary action buttons (like a delete `<button>` or `<a>`) inside this container, it creates invalid HTML (nested `<a>` tags) which severely breaks screen reader parsing and keyboard navigation.
**Action:** When a list item requires multiple interactive elements (like a file link and a delete button), always use a `<div>` for the `.list-group-item` container. Place the primary link as its own `<a>` element inside the container alongside the secondary actions.
