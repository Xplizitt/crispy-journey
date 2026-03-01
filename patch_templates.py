import re

with open('part_lister/templates/edit_part.html', 'r') as f:
    content = f.read()

# Add part_type to edit_part.html
part_type_html = """
        <div class="mb-3">
            <label for="part_type" class="form-label">Part Type:</label>
            <select class="form-select" name="part_type" id="part_type">
                <option value="Purchased" {% if part['part_type'] == 'Purchased' %}selected{% endif %}>Purchased</option>
                <option value="Raw Material" {% if part['part_type'] == 'Raw Material' %}selected{% endif %}>Raw Material</option>
                <option value="Manufactured" {% if part['part_type'] == 'Manufactured' %}selected{% endif %}>Manufactured</option>
                <option value="Assembly" {% if part['part_type'] == 'Assembly' %}selected{% endif %}>Assembly</option>
            </select>
        </div>
"""
content = content.replace('<div class="mb-3">\n            <label for="category"', part_type_html + '        <div class="mb-3">\n            <label for="category"')

# Add BOM management to edit_part.html if Manufactured or Assembly
bom_html = """
        <hr>
        {% if part['part_type'] in ['Manufactured', 'Assembly'] %}
        <div class="mb-4">
            <h2>Bill of Materials (BOM)</h2>
            <table class="table table-sm">
                <thead>
                    <tr>
                        <th>Child Part</th>
                        <th>Required Qty</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    {% for comp in bom_components %}
                    <tr>
                        <td>{{ comp['barcode'] }} - {{ comp['description'] }}</td>
                        <td>{{ comp['quantity_required'] }}</td>
                        <td>
                            <form method="post" action="{{ url_for('admin_bp.remove_bom_component', bom_id=comp['id']) }}" style="display:inline;">
                                <input type="hidden" name="parent_part_id" value="{{ part['id'] }}">
                                <button type="submit" class="btn btn-sm btn-danger" onclick="return confirm('Remove component?');">Remove</button>
                            </form>
                        </td>
                    </tr>
                    {% else %}
                    <tr><td colspan="3">No components added yet.</td></tr>
                    {% endfor %}
                </tbody>
            </table>

            <h4>Add Component</h4>
            <form method="post" action="{{ url_for('admin_bp.add_bom_component', part_id=part['id']) }}" class="row g-3 align-items-center">
                <div class="col-auto">
                    <input type="text" class="form-control" name="child_barcode" placeholder="Child Barcode" required>
                </div>
                <div class="col-auto">
                    <input type="number" step="0.01" class="form-control" name="quantity_required" placeholder="Qty Required (e.g., 1.5)" required>
                </div>
                <div class="col-auto">
                    <button type="submit" class="btn btn-success">Add</button>
                </div>
            </form>
        </div>
        {% endif %}
"""

content = content.replace("<h2>Attachments</h2>", bom_html + "\n            <h2>Attachments</h2>")

with open('part_lister/templates/edit_part.html', 'w') as f:
    f.write(content)


with open('part_lister/templates/part_view.html', 'r') as f:
    content = f.read()

part_type_view_html = """
                    <tr>
                        <th scope="row">Part Type</th>
                        <td>{{ part['part_type'] }}</td>
                    </tr>"""

content = content.replace('                    <tr>\n                        <th scope="row">Category</th>', part_type_view_html + '\n                    <tr>\n                        <th scope="row">Category</th>')

bom_view_html = """
            {% if part['part_type'] in ['Manufactured', 'Assembly'] %}
            <h2>Bill of Materials</h2>
            {% if bom_components %}
                <table class="table table-sm">
                    <thead>
                        <tr>
                            <th>Component</th>
                            <th>Qty Required</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for comp in bom_components %}
                        <tr>
                            <td><a href="{{ url_for('admin_bp.part_view', part_id=comp['child_part_id']) }}">{{ comp['barcode'] }} - {{ comp['description'] }}</a></td>
                            <td>{{ comp['quantity_required'] }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                <div class="card mt-3 mb-4">
                    <div class="card-body">
                        <h5 class="card-title">Build Units</h5>
                        <form method="post" action="{{ url_for('admin_bp.build_part', part_id=part['id']) }}" class="row g-3 align-items-center">
                            <div class="col-auto">
                                <label for="build_quantity" class="visually-hidden">Quantity</label>
                                <input type="number" min="1" step="1" class="form-control" id="build_quantity" name="build_quantity" placeholder="Quantity to Build" required>
                            </div>
                            <div class="col-auto">
                                <button type="submit" class="btn btn-success">Build</button>
                            </div>
                        </form>
                    </div>
                </div>
            {% else %}
                <p>No BOM defined.</p>
            {% endif %}
            {% endif %}
"""

content = content.replace("            <h2>Photo Gallery</h2>", bom_view_html + "\n            <h2>Photo Gallery</h2>")

with open('part_lister/templates/part_view.html', 'w') as f:
    f.write(content)


with open('part_lister/templates/admin.html', 'r') as f:
    content = f.read()

if 'part_type' not in content:
    content = content.replace("<th>UOM</th>", "<th>UOM</th>\n                <th>Type</th>")
    content = content.replace("<td>{{ part.uom }}</td>", "<td>{{ part.uom }}</td>\n                <td>{{ part.part_type }}</td>")

with open('part_lister/templates/admin.html', 'w') as f:
    f.write(content)
