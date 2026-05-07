# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.
## 2025-05-07 - Visually engaging empty states
**Learning:** Replaced the plain "No items in list" text with a styled empty state containing an icon (`bi-inbox`), a clear heading, and helper text ("Scan a barcode..."). This makes the empty state much more engaging and guides the user on what to do next. It is also important to update any frontend DOM-updating JavaScript logic (`app.js`) to ensure it outputs the exact same updated empty state HTML markup when it clears an emptied list dynamically.
**Action:** Always consider using visually appealing empty states with guidance in lists and tables instead of plain text placeholders to improve UX.
