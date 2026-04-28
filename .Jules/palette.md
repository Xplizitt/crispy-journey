# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.

## 2024-05-20 - Avoid Nested Interactive Elements
**Learning:** Nesting interactive elements like `<button>` or `<a>` inside a parent `<a>` tag creates invalid HTML that breaks screen reader accessibility and makes Playwright locators unreliable, as standard tools cannot properly determine the interaction target.
**Action:** When creating lists with both primary actions (like download/view) and secondary actions (like delete/edit), use non-interactive containers (like `<div>` or `<li>`) and place discrete UI actions into separate sibling tags, applying ARIA labels to icon-only buttons for full accessibility.
