with open("part_lister/templates/admin.html", "r") as f:
    text = f.read()

# I might have removed the first instance, which is the CORRECT one!
# Let's restore the top of the file to be correct.

# Prepend the correct header
correct_header = """{% extends 'base.html' %}

{% block title %}Admin Dashboard{% endblock %}

{% block content %}
"""

# Now remove ANY `{% extends 'base.html' %}` or `{% extends "base.html" %}` from text
import re
text = re.sub(r'\{% extends [\'"]base.html[\'"] %\}', '', text)
text = re.sub(r'\{% block title %\}.*?\{% endblock %\}', '', text, flags=re.S)
text = re.sub(r'\{% block content %\}', '', text)

# The endblock should just be at the end. We'll strip any existing endblocks that aren't inside loops.
# Actually, the only other blocks are `{% endblock %}`. Let's remove them all and add one at the very end.
text = re.sub(r'\{% endblock %\}', '', text)

with open("part_lister/templates/admin.html", "w") as f:
    f.write(correct_header + text + "\n{% endblock %}\n")
