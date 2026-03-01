import re

with open('part_lister/templates/edit_part.html', 'r') as f:
    content = f.read()

# Extract the BOM html block
bom_start = content.find("        <hr>\n        {% if part['part_type'] in ['Manufactured', 'Assembly'] %}")
bom_end = content.find("        {% endif %}\n") + len("        {% endif %}\n")

bom_html = content[bom_start:bom_end]

# Remove it from its current position
content = content[:bom_start] + content[bom_end:]

# Insert it at the end of the col-md-8 block, right before its closing div
col_8_end = content.find('            </form>\n        </div>') + len('            </form>\n')
content = content[:col_8_end] + bom_html + content[col_8_end:]

with open('part_lister/templates/edit_part.html', 'w') as f:
    f.write(content)
