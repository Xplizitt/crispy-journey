# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.

## 2025-06-09 - Structured Empty States
**Learning:** Plain text empty states (like "No items in list.") miss an opportunity to guide the user. Replacing them with a structured empty state component that includes a descriptive icon and clear instructional text provides better visual feedback and actionable next steps.
**Action:** When encountering empty tables or lists, implement a structured empty state component with an icon (e.g., `bi-box-seam`), a clear title, and instructional text instead of plain text. Ensure dynamic updates (like polling) use the exact same markup as server-rendered HTML.
