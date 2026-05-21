# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## 2025-05-21 - Icon-only Buttons Missing Accessible Names
**Learning:** Across this app, developers frequently use Bootstrap icons (e.g. `bi-trash`, `bi-eye`) and symbols (`&lt;`, `&gt;`) inside `<button>` or `<a>` tags without any text content, `aria-label`, or `title` attributes. This causes screen readers to read the button's action ambiguously or not at all, and deprives sighted users of mouse hover tooltips for context.
**Action:** When adding or reviewing icon-only actions (like delete, view, next/prev), always proactively ensure they include both a descriptive `aria-label` and `title`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.
