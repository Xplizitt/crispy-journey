# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.

## 2024-04-10 - Fix Nested Interactive Elements
**Learning:** Screen readers and automated locators fail to parse or interact with nested interactive elements, such as `<button>` tags or interactive `<i>` icons nested inside `<a>` tags. This creates a critical accessibility block where users and tests cannot trigger the intended secondary action (e.g., delete) without inadvertently triggering the primary action (e.g., download/navigate).
**Action:** Always place discrete interactive elements as sibling nodes within a semantic container (like a `<div>` or `<li>`), never nesting an `<a>` inside another `<a>` or a `<button>` inside an `<a>`.
