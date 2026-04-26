# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.

## 2024-04-26 - Nested Interactive Elements inside Lists
**Learning:** Avoid nesting `<a>` tags or interactive elements like buttons inside parent `<a>` tags in HTML/Jinja templates (e.g., list group items). This creates invalid HTML that browsers attempt to auto-correct unpredictably, which breaks screen reader accessibility, keyboard navigation, and Playwright locators.
**Action:** Use a non-interactive wrapper container like `<div>` or `<li>` with Flexbox utilities, and place the discrete UI actions (like the view link and delete button) as separate sibling elements within the container. Always add `text-truncate` and `title` to variable-length text links, and ensure icon-only action buttons have `aria-label` and `title`.
