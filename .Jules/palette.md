# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.
## 2024-05-18 - Fix invalid nested anchor tag
**Learning:** Invalid nested HTML tags (like `<a>` inside `<a>`) can cause accessibility issues and affect how screen readers parse content.
**Action:** Ensure valid HTML structure by replacing nested `<a>` tags with alternative layout structures like separate `<div>` containers or using buttons.
