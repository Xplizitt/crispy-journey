# Whoops! I replaced all `{% endblock %}` which includes `{% endblock %}` for `{% block title %}` which I also stripped. But wait, `{% for ... %}` uses `{% endfor %}`, `{% if ... %}` uses `{% endif %}`.
# Did the script remove `{% endif %}` or `{% endfor %}`? Let's check.
import re
with open("part_lister/templates/admin.html", "r") as f:
    text = f.read()

print("FOR blocks:", len(re.findall(r'\{% for ', text)))
print("ENDFOR blocks:", len(re.findall(r'\{% endfor %\}', text)))

print("IF blocks:", len(re.findall(r'\{% if ', text)))
print("ENDIF blocks:", len(re.findall(r'\{% endif %\}', text)))
