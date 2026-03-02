with open("part_lister/templates/admin.html", "r") as f:
    text = f.read()

# Replace the inner {% extends "base.html" %} and {% block title %}...{% endblock %} from the original file
import re
text = re.sub(r'\{% extends "base\.html" %\}\s*\{% block title %\}Admin - Part Management', '', text)

# Find the next {% endblock %} which belongs to the old title
# Actually, wait, the original admin.html has:
# {% extends "base.html" %}
# {% block title %}Admin - Part Management{% endblock %}
# {% block content %}

text = re.sub(r'\{% extends "base\.html" %\}', '', text)
text = re.sub(r'\{% block title %\}Admin - Part Management\{% endblock %\}', '', text)
text = text.replace('{% block content %}', '', 1) # remove the second block content
# Actually, let's just use string replace.

with open("part_lister/templates/admin.html", "w") as f:
    f.write(text)
