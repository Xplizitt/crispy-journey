with open("part_lister/templates/admin.html", "r") as f:
    text = f.read()

# We need to remove the duplicate `{% extends "base.html" %}` and `{% block title %}` / `{% block content %}` from the middle of the file.
text = text.replace('{% extends "base.html" %}', '', 1)
import re
text = re.sub(r'\{% block title %\}.*?\{% endblock %\}', '', text, count=1, flags=re.S)
text = text.replace('{% block content %}', '', 1)

with open("part_lister/templates/admin.html", "w") as f:
    f.write(text)
