# Palette UX Learnings

## Icons for Actions
- When replacing text-based buttons (like "Edit" or "Delete") with icon-only buttons, it is critical to include `aria-label` attributes to ensure the buttons remain accessible to screen readers. For example: `<a href="..." aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>`.

## Layout and Spacing
- Adding `align-middle` to Bootstrap tables ensures that text in rows containing thumbnail images aligns properly with the center of the image, significantly improving the visual appearance of the list.
- Adding a subtle shadow (`shadow-sm`) to main content containers helps separate the content from the background, adding depth to the page layout.

## 2026-06-17 - Improve Empty States
**Learning:** Replacing plain text empty states (like "No items in list.") with structured visual components (including icons, clear titles, and calls-to-action) makes the interface much more inviting and guides the user on what to do next. When updating server-side templates with these empty states, it is crucial to symmetrically update any client-side JavaScript that dynamically renders the same data to prevent jarring UI inconsistencies. Additionally, E2E tests containing hardcoded assertions for the old text must be updated to match the new structured content.
**Action:** Always check if a data table or list has an empty state. If it's just plain text, propose upgrading it to a structured component. Ensure symmetry between Jinja templates and JavaScript renderers, and update associated E2E assertions.
