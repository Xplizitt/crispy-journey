# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.
## 2026-05-15 - Fix Nested Links for File Attachments
**Learning:** Nesting `<a>` tags inside other `<a>` tags in Jinja templates (like placing a delete button inside a list item link) creates invalid HTML. This breaks screen reader accessibility and causes unpredictable layout behavior, especially with flexbox. It also makes Playwright testing difficult.
**Action:** Always use a non-interactive container (like `<div>` or `<li>`) for list items that require multiple distinct actions. Apply `d-flex justify-content-between align-items-center` to the container, and ensure individual actions (like download links and delete buttons) are separate `<a>` tags.
