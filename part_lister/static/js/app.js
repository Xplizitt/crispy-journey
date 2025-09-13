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

        applyThumbnailVisibility();

        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => {
                showThumbnails = !showThumbnails;
                localStorage.setItem('showThumbnails', showThumbnails);
                applyThumbnailVisibility();
            });
        }

        if (printToggleBtn) {
            printToggleBtn.addEventListener('click', () => {
                showThumbnails = !showThumbnails;
                applyThumbnailVisibility();
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

    // Run on page load
    document.addEventListener('DOMContentLoaded', function() {
        setupTitleUpdates();
        setupThumbnailToggle();
        setupThemeSwitcher();
        setupBulkEdit();

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
