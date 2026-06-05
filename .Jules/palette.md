# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.

## 2026-06-05 - Empty States
**Learning:** Plain text empty states (like "No items in list.") miss an opportunity to guide users on what to do next. Users may be confused about how to populate the table.
**Action:** Implement structured empty state components that include a descriptive icon, a clear title, and instructional text explaining how to populate the data.
