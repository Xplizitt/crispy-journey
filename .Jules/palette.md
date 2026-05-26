# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.

## 2025-05-26 - Empty State Pattern
**Learning:** Replaced plain text 'No items' rows with structured empty state components to improve user orientation and aesthetics. Providing a relevant icon, title, and clear call-to-action is a recognizable pattern that encourages users to engage with empty systems rather than wondering if the data is broken. Additionally, when using client-side table rendering (like in `app.js`), the exact server-side HTML for the empty state must be duplicated locally to ensure UI consistency before and after data refreshes.
**Action:** When creating lists or tables, immediately establish an empty state containing an icon, title, and actionable text. Ensure it is synced between server-side templates and client-side javascript rendering.
