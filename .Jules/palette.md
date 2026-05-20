# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.

## 2024-05-20 - Empty States
**Learning:** Empty states (like "No items in list") can feel stark. Enhancing them with center-aligned text, a subtle icon (like an inbox or box), and helpful guidance (e.g., "Scan a barcode or enter it above to add items") greatly improves the user experience and provides clear calls to action.
**Action:** Ensure empty state messages in tables and lists use these enhanced layout patterns consistently across server-rendered templates and client-side JavaScript.
