# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.

## 2026-04-06 - Fixing nested links and missing aria-labels on attachment delete buttons
**Learning:** Nested interactive elements (like an `<a>` tag inside another `<a>` tag) create invalid HTML and cause issues for screen readers and automated testing tools (like Playwright). Additionally, icon-only buttons need an `aria-label` and `title` for context.
**Action:** Always verify that interactive elements are not nested, using a `<div>` with `list-group-item` classes instead of an `<a>` wrapper if there are multiple click targets inside. Ensure all icon-only buttons include an `aria-label` and `title`.
