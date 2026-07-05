# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.

## 2024-11-20 - Structured Empty States
**Learning:** Replaced a plain text empty state ("No items in list.") with a structured empty state component that includes a descriptive icon (`bi-box-seam`), a clear title, and instructional text explaining how to populate the data. This provides better user guidance when there's no data. Note that when server-side HTML is updated for empty states, the client-side JavaScript rendering the exact same element dynamically must also be identically updated.
**Action:** Use this structured pattern (icon, title, instructions) across all tables/lists that can have an empty state in the app. Ensure JS client-side template literal is kept in sync with Jinja2 HTML.
