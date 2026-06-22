# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.
## 2026-06-22 - Empty State UI Enhancement
**Learning:** Replaced plain text empty states (like "No items in list.") with structured, user-friendly empty states containing an icon (`bi-box-seam`), a clear title, and instructional text, significantly improving the intuitiveness and look of empty tables. Crucially, the implementation must be synchronized across server-rendered Jinja2 templates (using `{% else %}`) and dynamic client-side JS rendering logic (`app.js` table clearing).
**Action:** Always implement empty states with an icon and call to action instead of plain text strings, and ensure E2E tests are updated to assert on the new structured text content instead of the old strings.
