def patch_wo_templates():
    # Work Orders Index HTML
    with open('part_lister/templates/work_orders/index.html', 'r') as f:
        content = f.read()

    wo_add_customer = """
                    <div class="mb-3">
                        <label for="customer_id" class="form-label">Customer</label>
                        <select class="form-select" id="customer_id" name="customer_id">
                            <option value="">-- None --</option>
                            {% for customer in customers %}
                            <option value="{{ customer.id }}">{{ customer.name }}</option>
                            {% endfor %}
                        </select>
                    </div>
"""
    content = content.replace('                            <label for="description" class="form-label">Description</label>\n                            <textarea class="form-control" id="description" name="description" rows="3"></textarea>\n                        </div>', '                            <label for="description" class="form-label">Description</label>\n                            <textarea class="form-control" id="description" name="description" rows="3"></textarea>\n                        </div>\n' + wo_add_customer)

    # Add Customer Column to table
    content = content.replace('<th>Title</th>\n                <th>Description</th>', '<th>Title</th>\n                <th>Customer</th>\n                <th>Description</th>')
    content = content.replace('<td>{{ wo.title }}</td>\n                <td>{{ wo.description[:50] }}{% if wo.description|length > 50 %}...{% endif %}</td>', '<td>{{ wo.title }}</td>\n                <td>\n                    {% if wo.customer_id %}\n                        <a href="{{ url_for(\'customers_bp.view\', customer_id=wo.customer_id) }}">{{ wo.customer_name }}</a>\n                    {% else %}\n                        <span class="text-muted">None</span>\n                    {% endif %}\n                </td>\n                <td>{{ wo.description[:50] }}{% if wo.description|length > 50 %}...{% endif %}</td>')

    with open('part_lister/templates/work_orders/index.html', 'w') as f:
        f.write(content)

    # Work Orders View HTML
    with open('part_lister/templates/work_orders/view.html', 'r') as f:
        content = f.read()

    wo_view_customer = """
                    <li class="list-group-item">
                        <strong><i class="bi bi-person"></i> Customer:</strong><br>
                        {% if work_order.customer_id %}
                            <a href="{{ url_for('customers_bp.view', customer_id=work_order.customer_id) }}">{{ work_order.customer_name }}</a>
                        {% else %}
                            <span class="text-muted">None</span>
                        {% endif %}
                    </li>
"""
    content = content.replace('<ul class="list-group list-group-flush">\n                    <li class="list-group-item">', '<ul class="list-group list-group-flush">\n' + wo_view_customer + '                    <li class="list-group-item">')

    with open('part_lister/templates/work_orders/view.html', 'w') as f:
        f.write(content)

patch_wo_templates()
