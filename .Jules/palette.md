# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.

## 2025-03-08 - Structured Empty States
**Learning:** Plain text empty states in tables or lists ("No items found") feel unfinished and offer poor guidance to the user.
**Action:** Always replace plain text empty states with a structured empty state component. This should include a descriptive icon (e.g., `bi-box-seam` for lists), a clear title ("Your list is empty"), and instructional text explaining how to populate the data. Ensure this structure is applied consistently across both server-rendered HTML (Jinja2) and client-side JavaScript rendering.
