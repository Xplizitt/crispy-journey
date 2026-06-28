# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.
## 2024-03-24 - Accessibility and Locators break with Nested Interactive Elements
**Learning:** Nesting interactive elements (like an `<a>` inside an `<a>` tag, as was present in the attachment list) creates invalid HTML. This not only breaks screen reader accessibility by confusing the focus and interaction order, but it also causes Playwright locators to fail because the browser tries to autocorrect the DOM, restructuring the elements unexpectedly.
**Action:** When rendering lists or items that have primary actions (like downloading a file) and secondary actions (like deleting the file) side-by-side, always use a non-interactive container element (like a `<div>`) as the wrapper, and place the distinct `<a>` or `<button>` elements within it.
