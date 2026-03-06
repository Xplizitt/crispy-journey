# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.

## 2025-09-16 - Prevent Invalid HTML with Nested Interactive Elements
**Learning:** Avoid nesting interactive elements like `<a>` inside other `<a>` tags. This is invalid HTML and causes screen readers to have difficulty interpreting the interactive areas, leading to poor accessibility.
**Action:** When an entire list item needs to be clickable but also contain secondary actions (like a delete button), use a non-interactive wrapper (e.g., `<div>` or `<li>`) for the container and place the primary link and secondary actions as siblings within it. Also, always remember to add `aria-label` to icon-only buttons.
