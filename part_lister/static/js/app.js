/*
 * Part Lister - Main JavaScript file for the primary user interface.
 *
 * Project Overview:
 * This application allows users to manage a database of parts and create pick lists.
 * This file contains the JavaScript for the main, modern interface, which uses Bootstrap 5.
 * It is NOT used by the simplified scanner interface.
 *
 * Core Technologies:
 * - Backend: Flask (Python)
 * - Database: SQLite
 * - Frontend (Main Interface): Bootstrap 5, Jinja2 templates
 *
 * Key Features Handled by this File:
 * - AJAX for adding parts and list items without a full page reload.
 * - Dynamic updates to the UI (e.g., toggling thumbnails with button state, theme switching).
 * - Handling for the image gallery modal on the Part View page.
 * - Automatic polling for list updates on the main list page (also updates item count badge).
 * - Bootstrap Toast notification after barcode add-to-list.
 * - Inline stock quantity editing in admin table (saves via fetch on change).
 * - Drag-and-drop upload zone on gallery page.
 *
 * Notes for Future Agents:
 * - Please update this header comment with any major changes or new requirements.
 * - This file is for the main interface only. Do not add code here that is intended for the scanner interface.
 * - The scanner interface (`scanner.html`) contains its own, simplified JavaScript.
 * - The code uses modern JavaScript features that are not compatible with old browsers like IE on Windows CE.
 */
(function() {
    var originalTitle = document.title;

    function onInputFocus(event) {
        var target = event.target || event.srcElement;
        var inputName = target.id || target.name;
        if (inputName) {
            var capitalizedInputName = inputName.charAt(0).toUpperCase() + inputName.slice(1);
            document.title = originalTitle + ' - ' + capitalizedInputName;
        }
    }

    function onInputBlur() {
        document.title = originalTitle;
    }

    window.setupTitleUpdates = function() {
        var inputs = document.getElementsByTagName('input');
        for (var i = 0; i < inputs.length; i++) {
            if (inputs[i].type !== 'submit' && inputs[i].type !== 'hidden') {
                if (inputs[i].addEventListener) {
                    inputs[i].addEventListener('focus', onInputFocus);
                    inputs[i].addEventListener('blur', onInputBlur);
                } else if (inputs[i].attachEvent) { // IE8 and below
                    inputs[i].attachEvent('onfocus', onInputFocus);
                    inputs[i].attachEvent('onblur', onInputBlur);
                }
            }
        }
    };

    window.setupEnterKeyRedirect = function(formId, fromId, toId) {
        var fromElement = document.getElementById(fromId);
        var toElement = document.getElementById(toId);
        var formElement = document.getElementById(formId);

        if (fromElement && toElement && formElement) {
            var onKeyDown = function(event) {
                if (event.keyCode === 13) {
                    var target = event.target || event.srcElement;
                    if (target.id === fromId) {
                        event.preventDefault ? event.preventDefault() : (event.returnValue = false);
                        toElement.focus();
                    }
                }
            };
            if (fromElement.addEventListener) {
                fromElement.addEventListener('keydown', onKeyDown);
            } else if (fromElement.attachEvent) {
                fromElement.attachEvent('onkeydown', onKeyDown);
            }
        }
    };

    function setupThumbnailToggle() {
        const toggleBtn = document.getElementById('toggle-thumbnails-btn');
        const printToggleBtn = document.getElementById('toggle-thumbnails-btn-print');
        const thumbnailCols = document.querySelectorAll('.thumbnail-col');
        let showThumbnails = localStorage.getItem('showThumbnails') !== 'false';

        function applyThumbnailVisibility() {
            thumbnailCols.forEach(col => {
                col.style.display = showThumbnails ? '' : 'none';
            });
        }

        function updateToggleBtnState(btn) {
            if (!btn) return;
            if (showThumbnails) {
                btn.textContent = 'Hide Thumbnails';
                btn.classList.remove('btn-outline-secondary');
                btn.classList.add('btn-secondary');
            } else {
                btn.textContent = 'Show Thumbnails';
                btn.classList.remove('btn-secondary');
                btn.classList.add('btn-outline-secondary');
            }
        }

        applyThumbnailVisibility();
        updateToggleBtnState(toggleBtn);
        updateToggleBtnState(printToggleBtn);

        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => {
                showThumbnails = !showThumbnails;
                localStorage.setItem('showThumbnails', showThumbnails);
                applyThumbnailVisibility();
                updateToggleBtnState(toggleBtn);
            });
        }

        if (printToggleBtn) {
            printToggleBtn.addEventListener('click', () => {
                showThumbnails = !showThumbnails;
                applyThumbnailVisibility();
                updateToggleBtnState(printToggleBtn);
            });
        }
    }

    function setupThemeSwitcher() {
        const themeSwitcher = document.getElementById('theme-switcher');
        const dropdownItems = document.querySelectorAll('[data-theme]');
        const body = document.body;

        const setTheme = (theme) => {
            if (theme === 'dark') {
                body.classList.add('dark-theme');
            } else {
                body.classList.remove('dark-theme');
            }
            localStorage.setItem('theme', theme);
        };

        dropdownItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const theme = item.getAttribute('data-theme');
                setTheme(theme);
            });
        });

        // Apply saved theme on page load
        const savedTheme = localStorage.getItem('theme') || 'light';
        setTheme(savedTheme);
    }

    function setupBulkEdit() {
        const selectAllCheckbox = document.getElementById('select-all-checkbox');
        const partCheckboxes = document.querySelectorAll('.part-checkbox');

        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', (e) => {
                partCheckboxes.forEach(checkbox => {
                    checkbox.checked = e.target.checked;
                });
            });
        }
    }

    function showAddToast(message) {
        const toastEl = document.getElementById('add-item-toast');
        if (!toastEl) return;
        document.getElementById('add-item-toast-body').textContent = message;
        const toast = bootstrap.Toast.getOrCreateInstance(toastEl);
        toast.show();
    }

    function setupAjaxAddToList() {
        const form = document.getElementById('add-item-form');
        if (!form) return;

        form.addEventListener('submit', function(event) {
            event.preventDefault();

            const formData = new FormData(form);
            const barcode = formData.get('barcode');
            const quantity = formData.get('quantity');
            const add_as_separate = document.getElementById('add_as_separate').checked;

            fetch('/add_to_list', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    barcode: barcode,
                    quantity: quantity,
                    add_as_separate: add_as_separate
                }),
            })
            .then(response => response.json())
            .then(data => {
                const alertContainer = document.getElementById('alert-container');
                alertContainer.innerHTML = ''; // Clear previous alerts

                if (data.error) {
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'alert alert-danger';
                    errorDiv.textContent = data.error;
                    alertContainer.appendChild(errorDiv);
                } else {
                    pollList(); // Refresh the list
                    form.reset();
                    const barcodeInput = document.getElementById('barcode');
                    if (barcodeInput) { barcodeInput.focus(); barcodeInput.select(); }
                    if (data.success) {
                        showAddToast('Quantity updated for ' + barcode);
                    } else {
                        showAddToast('Added: ' + (data.description || barcode));
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                const alertContainer = document.getElementById('alert-container');
                alertContainer.innerHTML = '<div class="alert alert-danger">An unexpected error occurred.</div>';
            });
        });
    }

    function setupAjaxAddPart() {
        const form = document.querySelector('#adminAccordion form[action="/add_part"]');
        if (!form) return;

        form.addEventListener('submit', function(event) {
            event.preventDefault();

            const formData = new FormData(form);

            fetch('/add_part', {
                method: 'POST',
                body: formData, // No 'Content-Type' header needed, browser sets it for FormData
            })
            .then(response => response.json())
            .then(data => {
                const adminAlertContainer = document.getElementById('admin-alert-container');
                adminAlertContainer.innerHTML = ''; // Clear previous alerts

                if (data.error) {
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'alert alert-danger';
                    errorDiv.textContent = data.error;
                    adminAlertContainer.appendChild(errorDiv);
                } else {
                    const successDiv = document.createElement('div');
                    successDiv.className = 'alert alert-success';
                    successDiv.textContent = `Successfully added part: ${data.description}`;
                    adminAlertContainer.appendChild(successDiv);

                    const tableBody = document.querySelector('.table tbody');
                    const newRow = document.createElement('tr');

                    let attachmentLinks = '';
                    if (data.attachments) {
                        attachmentLinks = data.attachments.split(',').map(name =>
                            `<a href="/uploads/${name}" target="_blank">${name}</a>`
                        ).join('<br>');
                    }

                    newRow.innerHTML = `
                        <td><input type="checkbox" name="part_ids" value="${data.id}" class="part-checkbox"></td>
                        <td class="thumbnail-col">${data.thumbnail ? `<img src="/thumbnails/${data.thumbnail}" alt="Thumbnail" width="100">` : ''}</td>
                        <td>${data.barcode}</td>
                        <td>${data.description}</td>
                        <td>${data.part_number || ''}</td>
                        <td>${data.uom || ''}</td>
                        <td>${data.supplier_name || ''}</td>
                        <td>${data.notes || ''}</td>
                        <td>${attachmentLinks}</td>
                        <td>
                            <a href="/edit_part/${data.id}" class="btn btn-sm btn-outline-primary" aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>
                            <a href="/delete_part/${data.id}" class="btn btn-sm btn-outline-danger" onclick="return confirm('Are you sure you want to delete this part?');" aria-label="Delete" title="Delete"><i class="bi bi-trash"></i></a>
                        </td>
                    `;
                    tableBody.prepend(newRow);

                    form.reset();
                }
            })
            .catch(error => {
                console.error('Error:', error);
                const adminAlertContainer = document.getElementById('admin-alert-container');
                adminAlertContainer.innerHTML = '<div class="alert alert-danger">An unexpected error occurred.</div>';
            });
        });
    }

    function renderListTable(items) {
        const tableBody = document.querySelector('.table tbody');
        if (!tableBody) return;

        // Clear existing rows
        tableBody.innerHTML = '';

        if (items.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="8" class="text-center py-5 text-muted">
                        <i class="bi bi-inbox fs-1 d-block mb-3 text-secondary"></i>
                        <h4 class="mb-2">Your list is empty</h4>
                        <p class="mb-0">Scan a barcode or enter one above to add items to your list.</p>
                    </td>
                </tr>
            `;
            return;
        }

        items.forEach(item => {
            const newRow = document.createElement('tr');
            newRow.innerHTML = `
                <td class="thumbnail-col">${item.thumbnail ? `<img src="/thumbnails/${item.thumbnail}" alt="Thumbnail" width="100">` : ''}</td>
                <td>${item.barcode}</td>
                <td>${item.description}</td>
                <td><a href="/part/${item.part_id}">${item.part_number}</a></td>
                <td>${item.uom || ''}</td>
                <td>${item.supplier_name || ''}</td>
                <td>${item.quantity}</td>
                <td>
                    <a href="/edit_list_item/${item.id}" class="btn btn-sm btn-outline-primary" aria-label="Edit" title="Edit"><i class="bi bi-pencil"></i></a>
                    <a href="/delete_list_item/${item.id}" class="btn btn-sm btn-outline-danger" aria-label="Delete" title="Delete"><i class="bi bi-trash"></i></a>
                </td>
            `;
            tableBody.appendChild(newRow);
        });
    }

    function pollList() {
        const tableBody = document.querySelector('.table tbody');
        if (!tableBody || !tableBody.dataset.activeListId) return;
        const activeListId = tableBody.dataset.activeListId;

        fetch(`/api/lists/${activeListId}/items`)
            .then(response => response.json())
            .then(data => {
                renderListTable(data);
                const badge = document.getElementById('list-item-count-badge');
                if (badge) {
                    badge.textContent = data.length + (data.length === 1 ? ' item' : ' items');
                    badge.style.display = data.length > 0 ? '' : 'none';
                }
            })
            .catch(error => console.error('Polling error:', error));
    }

    function setupListPolling() {
        const tableBody = document.querySelector('.table tbody');
        if (!tableBody || !tableBody.dataset.activeListId) return;

        pollList(); // Poll immediately on page load
        setInterval(pollList, 5000); // Poll every 5 seconds
    }

    function setupInlineStockEdit() {
        document.addEventListener('change', function(e) {
            const input = e.target.closest('.inline-stock-edit');
            if (!input) return;

            const partId = input.dataset.partId;
            const newStock = parseInt(input.value, 10);
            if (isNaN(newStock)) return;

            input.disabled = true;
            fetch(`/update_stock/${partId}`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({stock_quantity: newStock})
            })
            .then(r => r.json())
            .then(data => {
                input.disabled = false;
                if (data.error) {
                    input.classList.add('is-invalid');
                } else {
                    input.classList.remove('is-invalid');
                    input.classList.add('is-valid');
                    setTimeout(() => input.classList.remove('is-valid'), 2000);
                }
            })
            .catch(() => {
                input.disabled = false;
                input.classList.add('is-invalid');
            });
        });
    }

    function setupGalleryDropZone() {
        const dropZone = document.getElementById('drop-zone');
        const fileInput = document.getElementById('files');
        const label = document.getElementById('drop-zone-label');
        if (!dropZone || !fileInput) return;

        dropZone.addEventListener('click', () => fileInput.click());

        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.style.background = 'rgba(13, 110, 253, 0.08)';
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.style.background = '';
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.style.background = '';
            const files = e.dataTransfer.files;
            fileInput.files = files;
            label.textContent = files.length + ' file' + (files.length !== 1 ? 's' : '') + ' selected';
        });

        fileInput.addEventListener('change', () => {
            const count = fileInput.files.length;
            label.textContent = count + ' file' + (count !== 1 ? 's' : '') + ' selected';
        });
    }

    // Run on page load
    function setupImageModal() {
        const imageModal = document.getElementById('imageModal');
        if (imageModal) {
            imageModal.addEventListener('show.bs.modal', function (event) {
                const link = event.relatedTarget;
                const imageSrc = link.getAttribute('data-image-src');
                const modalImage = imageModal.querySelector('#modalImage');
                modalImage.src = imageSrc;
            });
        }
    }

    // Run on page load
    document.addEventListener('DOMContentLoaded', function() {
        setupTitleUpdates();
        setupThumbnailToggle();
        setupThemeSwitcher();
        setupBulkEdit();
        setupAjaxAddToList();
        setupAjaxAddPart();
        setupListPolling();
        setupImageModal();
        setupInlineStockEdit();
        setupGalleryDropZone();

        // Specific setup for index page
        if (document.getElementById('add-item-form')) {
            setupEnterKeyRedirect('add-item-form', 'barcode', 'quantity');
            const barcodeInput = document.getElementById('barcode');
            if(barcodeInput) {
                barcodeInput.focus();
            }
        }
    });
})();
