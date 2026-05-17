## YYYY-MM-DD - Missing aria-labels on icon-only buttons
**Learning:** Found several Bootstrap icon-only `<a>` tags acting as buttons in Jinja2 templates (e.g., `bi-eye`, `bi-trash`) without `aria-label` or `title` attributes. This completely hides the button's purpose from screen readers and lacks visual tooltip context.
**Action:** Always ensure that whenever an interactive element lacks descriptive text, an `aria-label` (for screen readers) and a `title` (for mouse hover tooltips) are explicitly provided to improve both accessibility and general UX.
