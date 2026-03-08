def patch_templates():
    # Admin HTML
    with open('part_lister/templates/admin.html', 'r') as f:
        content = f.read()

    add_part_customer = """
                    <div class="col-md-6 mb-3">
                        <label for="customer_id" class="form-label">Customer</label>
                        <select class="form-select" id="customer_id" name="customer_id">
                            <option value="">-- None --</option>
                            {% for customer in customers %}
                            <option value="{{ customer.id }}">{{ customer.name }}</option>
                            {% endfor %}
                        </select>
                    </div>
"""
    content = content.replace('<label for="part_type" class="form-label">Part Type</label>\n                        <select class="form-select" id="part_type" name="part_type">\n                            <option value="Purchased">Purchased</option>\n                            <option value="Manufactured">Manufactured</option>\n                        </select>\n                    </div>', '<label for="part_type" class="form-label">Part Type</label>\n                        <select class="form-select" id="part_type" name="part_type">\n                            <option value="Purchased">Purchased</option>\n                            <option value="Manufactured">Manufactured</option>\n                        </select>\n                    </div>\n' + add_part_customer)

    with open('part_lister/templates/admin.html', 'w') as f:
        f.write(content)

    # Edit Part HTML
    with open('part_lister/templates/edit_part.html', 'r') as f:
        content = f.read()

    edit_part_customer = """
                    <div class="col-md-6 mb-3">
                        <label for="customer_id" class="form-label">Customer</label>
                        <select class="form-select" id="customer_id" name="customer_id">
                            <option value="">-- None --</option>
                            {% for customer in customers %}
                            <option value="{{ customer.id }}" {% if part.customer_id == customer.id %}selected{% endif %}>{{ customer.name }}</option>
                            {% endfor %}
                        </select>
                    </div>
"""
    content = content.replace('<label for="part_type" class="form-label">Part Type</label>\n                        <select class="form-select" id="part_type" name="part_type">\n                            <option value="Purchased" {% if part.part_type == \'Purchased\' %}selected{% endif %}>Purchased</option>\n                            <option value="Manufactured" {% if part.part_type == \'Manufactured\' %}selected{% endif %}>Manufactured</option>\n                        </select>\n                    </div>', '<label for="part_type" class="form-label">Part Type</label>\n                        <select class="form-select" id="part_type" name="part_type">\n                            <option value="Purchased" {% if part.part_type == \'Purchased\' %}selected{% endif %}>Purchased</option>\n                            <option value="Manufactured" {% if part.part_type == \'Manufactured\' %}selected{% endif %}>Manufactured</option>\n                        </select>\n                    </div>\n' + edit_part_customer)

    with open('part_lister/templates/edit_part.html', 'w') as f:
        f.write(content)

    # Part View HTML
    with open('part_lister/templates/part_view.html', 'r') as f:
        content = f.read()

    part_view_customer = """
                    <tr>
                        <th class="w-25 bg-light"><i class="bi bi-person"></i> Customer</th>
                        <td>
                            {% if part.customer_id %}
                                <a href="{{ url_for('customers_bp.view', customer_id=part.customer_id) }}">{{ part.customer_name }}</a>
                            {% else %}
                                <span class="text-muted">None</span>
                            {% endif %}
                        </td>
                    </tr>
"""
    content = content.replace('<tr>\n                        <th class="w-25 bg-light"><i class="bi bi-upc-scan"></i> Barcode</th>', part_view_customer + '\n                    <tr>\n                        <th class="w-25 bg-light"><i class="bi bi-upc-scan"></i> Barcode</th>')

    with open('part_lister/templates/part_view.html', 'w') as f:
        f.write(content)

patch_templates()
