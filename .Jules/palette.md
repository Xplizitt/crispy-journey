# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.

## 2026-04-24 - Nested Interactive Elements & Icon-Only Buttons Accessibility
**Learning:** Found an instance in `edit_part.html` where an interactive element (a delete `<button>`/`<a>`) was nested inside another `<a>` tag used for document viewing. This creates invalid HTML, breaks keyboard tab-navigation, and causes issues for screen readers. Also found multiple instances of icon-only action buttons (e.g., trash icons for log entries and task parts in `work_orders/view.html`) missing `aria-label` attributes.
**Action:** When designing lists with multiple actions per item (like viewing vs. deleting), wrap the item in a non-interactive container (like `<div>` or `<li>`) and make each action a distinct, separate interactive element (e.g., separate `<a>` or `<button>`). Ensure all icon-only buttons always have an explicit `aria-label` attribute describing their specific action.
