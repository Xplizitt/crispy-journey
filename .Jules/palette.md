# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.

## 2026-04-16 - Prevent Layout Breakage in Attachment Lists
**Learning:** In list views where users upload files with arbitrary names (like the attachment list in `edit_part.html`), extremely long filenames can overflow their containers or push interactive elements (like delete buttons) off-screen, breaking the layout and usability. Additionally, floating form labels (e.g., in the login form) should be targeted by Playwright without trailing colons.
**Action:** When designing lists that render user-generated text strings, proactively use truncation classes (like Bootstrap's `text-truncate`) and ensure a `title` attribute is present so the full text remains accessible on hover.
