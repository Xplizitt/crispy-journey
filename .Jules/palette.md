# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.

## 2026-06-03 - Structured Empty States
**Learning:** Plain text empty states like "No items in list." provide poor UX and feel unfinished.
**Action:** Replace plain text empty states in tables or lists with a structured empty state component that includes a descriptive icon (e.g., `bi-box-seam`), a clear title (e.g., "Your list is empty"), and instructional text explaining how to populate the data. When updating server-rendered HTML templates for these components, ensure any corresponding client-side JavaScript (e.g., dynamically rendering table contents) is identically updated to inject the exact same HTML markup.
