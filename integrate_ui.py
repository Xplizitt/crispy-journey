import re

with open("part_lister/templates/admin.html", "r") as f:
    original_admin = f.read()

# Extract the body parts of original_admin that represent the functionality
# e.g., <div class="accordion" id="adminAccordion">, the parts list table

# We will just insert the accordion and parts list into the main content area of stitch_admin.html.
# Actually, the user asked to "integrate the dashboard into the app".
# Let's take stitch_admin.html and make it a valid Jinja template extending base.html.

with open("stitch_admin.html", "r") as f:
    stitch_html = f.read()

# We need to extract the tailwind CDN and CSS from stitch_admin.html
# and put it into admin.html

new_admin_content = """{% extends 'base.html' %}

{% block title %}Admin Dashboard{% endblock %}

{% block content %}
<!-- Tailwind and Styles from Stitch -->
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet" />
<script id="tailwind-config">
    tailwind.config = {
        darkMode: "class",
        theme: {
            extend: {
                colors: {
                    "primary": "#137fec",
                    "background-light": "#f6f7f8",
                    "background-dark": "#101922",
                },
                fontFamily: {
                    "display": ["Inter", "sans-serif"]
                },
                borderRadius: {
                    "DEFAULT": "0.25rem",
                    "lg": "0.5rem",
                    "xl": "0.75rem",
                    "full": "9999px"
                },
            },
        },
        corePlugins: {
            preflight: false,
        }
    }
</script>
<style>
    /* Prevent Tailwind from overriding Bootstrap globals */
    .tw-wrapper {
        font-family: 'Inter', sans-serif;
    }
    .material-symbols-outlined {
        font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
    }
    /* Scope tailwind to .tw-wrapper to avoid messing up bootstrap */
</style>

<div class="tw-wrapper">
"""

# Extract the <div class="p-8 space-y-8 max-w-7xl mx-auto w-full"> from stitch_html
import bs4
soup = bs4.BeautifulSoup(stitch_html, "html.parser")
main_content = soup.find("main")

# Find the cards grid:
cards_div = main_content.find("div", class_=re.compile("grid grid-cols-1.*lg:grid-cols-4.*"))
if cards_div:
    new_admin_content += str(cards_div) + "\n"

new_admin_content += """
    <hr class="my-8">
"""

# Append original admin content here (which contains accordion and table)
original_content_stripped = original_admin.replace("{% extends 'base.html' %}", "").replace("{% block content %}", "").replace("{% endblock %}", "").strip()

new_admin_content += original_content_stripped

new_admin_content += """
</div>
{% endblock %}
"""

with open("part_lister/templates/admin.html", "w") as f:
    f.write(new_admin_content)
