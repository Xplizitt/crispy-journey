# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.

## 2026-06-02 - Structured Empty States
**Learning:** Replacing plain text empty states with structured components (icon, title, instructional text) makes tables feel more intentional and user-friendly, as plain text can often look like an error or broken state.
**Action:** Always implement a structured empty state component with a clear title and guidance for tables or lists.
