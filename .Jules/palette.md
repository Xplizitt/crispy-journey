# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.
## 2026-05-02 - Add ARIA Labels to Delete Icons
**Learning:** Found several `delete`/`trash` buttons represented only by a `<i class="bi bi-trash"></i>` icon across `edit_part.html` and `work_orders/view.html`. This pattern severely impacts screen reader users, who will just hear "button" without context of what it deletes.
**Action:** Applied `aria-label` to provide specific context ("Remove part", "Delete log", "Delete attachment") to these buttons. Will proactively check all `bi-trash` and `bi-pencil` icon-only buttons for missing `aria-label` attributes.
