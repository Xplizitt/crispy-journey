with open("part_lister/templates/admin.html", "r") as f:
    text = f.read()

# I removed {% block content %} entirely!
text = text.replace("{% block title %}Admin Dashboard{% endblock %}", "{% block title %}Admin Dashboard{% endblock %}\n{% block content %}")

with open("part_lister/templates/admin.html", "w") as f:
    f.write(text)
