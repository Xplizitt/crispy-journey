# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.
## 2026-05-03 - Icon-only buttons accessibility
**Learning:** Icon-only buttons used for actions like "Delete" or "Attach" within lists or collapsible headers lack context for both screen readers and visual users hovering over them. Adding `aria-label` provides aural context, and `title` provides visual context (tooltip).
**Action:** Always ensure `aria-label` and `title` are paired on any `<button>` or `<a>` tag that relies solely on an icon (`<i>` or `<img>`) for its affordance.
