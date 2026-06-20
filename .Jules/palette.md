# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.
## 2026-06-20 - Structured Empty States
**Learning:** Users easily overlook plain text empty states in data tables, and generic text ('No items in list.') provides poor affordance. Furthermore, when updating an HTML template, the dynamic JS rendering logic MUST be updated identically to prevent state divergence.
**Action:** Implemented a unified 'empty state' component across all major views using the `bi-box-seam` icon, a clear title, and instructional text, while ensuring `app.js` dynamically renders the exact same structure.
