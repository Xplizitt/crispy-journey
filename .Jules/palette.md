# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.

## 2025-05-15 - Structured Empty States
**Learning:** Using a structured empty state component with an icon, title, and descriptive text makes it clearer for users what to do next, compared to a plain "No items in list" text. It provides better visual hierarchy and feels more intentional.
**Action:** When replacing simple empty text states, replace it with a structured empty state component to provide a better UX. Ensure Jinja templates and JavaScript files generating HTML both use the identical structured markup for empty states.
