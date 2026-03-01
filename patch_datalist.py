import re

with open('part_lister/routes/admin.py', 'r') as f:
    content = f.read()

# Add all_parts query to edit_part GET
all_parts_query = """    bom_components = cur.fetchall()

    cur = db.execute('SELECT barcode, description FROM parts ORDER BY description')
    all_parts = cur.fetchall()

    return render_template('edit_part.html', part=part, attachments=attachments, bom_components=bom_components, all_parts=all_parts)"""

content = content.replace("    bom_components = cur.fetchall()\n\n    return render_template('edit_part.html', part=part, attachments=attachments, bom_components=bom_components)", all_parts_query)

with open('part_lister/routes/admin.py', 'w') as f:
    f.write(content)

with open('part_lister/templates/edit_part.html', 'r') as f:
    content = f.read()

# Add datalist to edit_part.html
datalist_html = """            <h4>Add Component</h4>
            <form method="post" action="{{ url_for('admin_bp.add_bom_component', part_id=part['id']) }}" class="row g-3 align-items-center">
                <div class="col-auto">
                    <input type="text" class="form-control" name="child_barcode" list="partList" placeholder="Child Barcode" autocomplete="off" required>
                    <datalist id="partList">
                        {% for p in all_parts %}
                        <option value="{{ p['barcode'] }}">{{ p['description'] }}</option>
                        {% endfor %}
                    </datalist>
                </div>"""

content = content.replace('''            <h4>Add Component</h4>
            <form method="post" action="{{ url_for('admin_bp.add_bom_component', part_id=part['id']) }}" class="row g-3 align-items-center">
                <div class="col-auto">
                    <input type="text" class="form-control" name="child_barcode" placeholder="Child Barcode" required>
                </div>''', datalist_html)

with open('part_lister/templates/edit_part.html', 'w') as f:
    f.write(content)
