# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.

## 2024-05-18 - Nested Interactive Elements in List Groups
**Learning:** Found a pattern where an entire Bootstrap `.list-group-item` was incorrectly used as an anchor `<a>` tag, containing nested interactive elements (like a delete `<button>` or `<a>`). This creates invalid HTML and causes screen readers to misinterpret the nested action, making it difficult or impossible to select the nested element.
**Action:** When using `.list-group-item` with multiple interactions (e.g., a main link and a secondary action like 'Delete'), use a `<div>` for the `.list-group-item` wrapper. Inside the wrapper, use flexbox utilities to separate a primary text link `<a>` from the secondary action button `<a>`.
