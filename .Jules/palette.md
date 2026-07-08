# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.

## 2026-07-08 - Structured Empty States
**Learning:** In tables or lists that might be empty, a completely blank table row or simple plain text like "No items in list" feels broken or unhelpful. When using server-rendered templates combined with client-side DOM updates (like `app.js` rewriting the table body), both states must render the exact same HTML to prevent layout shifts or inconsistent user experiences.
**Action:** Replace plain text empty states with a structured component that includes a descriptive icon (`bi-box-seam`), a clear title ("Your list is empty"), and instructional text. Ensure both Jinja2 templates (`{% else %}` blocks) and client-side JavaScript (`innerHTML`) inject identical markup.
