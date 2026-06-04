# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.

## 2026-06-04 - Empty States in Tables
**Learning:** Replacing plain text empty states (like "No items in list.") with structured components featuring a descriptive icon, clear title, and instructional text significantly improves the initial user experience by guiding them on how to populate the empty area.
**Action:** When working on tables or lists that can be empty, always check if there is an opportunity to replace a plain string with a more helpful, icon-driven empty state component that matches the design system.
