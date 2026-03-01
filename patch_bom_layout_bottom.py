import re

with open('part_lister/templates/edit_part.html', 'r') as f:
    content = f.read()

# Extract the BOM html block again and put it completely after the row div
bom_start = content.find("        <hr>\n        {% if part['part_type'] in ['Manufactured', 'Assembly'] %}")
bom_end = content.find("        {% endif %}\n") + len("        {% endif %}\n")

if bom_start != -1:
    bom_html = content[bom_start:bom_end]
    content = content[:bom_start] + content[bom_end:]

    row_end = content.find('        </div>\n    </div>\n{% endblock %}') + len('        </div>\n    </div>\n')

    content = content[:row_end] + "\n    <div class=\"row mt-4\">\n        <div class=\"col-12\">\n" + bom_html + "        </div>\n    </div>\n" + content[row_end:]

    with open('part_lister/templates/edit_part.html', 'w') as f:
        f.write(content)
