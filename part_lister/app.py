# Mile Marker: 2025-09-16 - Refactored using Flask Blueprints.
#
# Part Lister - A Flask-based application for managing parts and creating pick lists.
#
# Project Overview:
# This application allows users to manage a database of parts, including their details and attachments (images, DXF files, etc.).
# It provides a main interface for managing parts and a simplified interface for use on older devices like Windows CE scanners.
# Users can also create and manage pick lists of parts.
#
# Core Technologies:
# - Backend: Flask (Python)
# - Database: SQLite
# - Frontend (Main Interface): Bootstrap 5, Jinja2 templates
# - Frontend (Scanner Interface): Basic HTML and JavaScript for compatibility with older browsers (e.g., Internet Explorer on Windows CE 6.0).
#
# Key Features & Recent Changes (as of 2025-09-16):
# - Part Management: Add, edit, delete parts.
# - Part View: A detailed view for each part, with a photo gallery and a list of file attachments.
# - Scanner Interface: A simplified interface at `/scanner` for adding items to lists on devices with old browsers.
# - File Attachments: Supports various file types, including images and DXF files.
# - Thumbnail Support: Parts can have a thumbnail image.
#
# Notes for Future Agents:
# - Please update this header comment with any major changes or new requirements.
# - The application has two distinct user interfaces: the main one (using Bootstrap 5) and the scanner one (using basic HTML).
# - When making changes, consider the compatibility requirements for the scanner interface. Avoid using modern JavaScript/CSS features in `scanner.html` and related templates.
# - The `add_to_list` route has been modified to accept both JSON and form-urlencoded data to support both interfaces.
# - The `switch_list` route has been modified to redirect back to the referrer to support list switching from both interfaces.
# - 2025-09-16: Refactored app.py using Flask Blueprints. The business logic has been moved to part_lister/routes/ (admin.py, core.py, scanner.py).

import sqlite3
import os
from flask import Flask, g, url_for as original_url_for
from PIL import Image

try:
    from part_lister.database import init_db_migrations
except ImportError:
    from database import init_db_migrations

app = Flask(__name__)

# --- Configuration ---
_basedir = os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH = os.path.join(_basedir, '..', 'parts.db')
UPLOAD_FOLDER = os.path.join(_basedir, 'static', 'uploads')
THUMBNAIL_FOLDER = os.path.join(_basedir, 'static', 'thumbnails')

app.config['DATABASE'] = DATABASE_PATH
app.config['SECRET_KEY'] = 'dev'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['THUMBNAIL_FOLDER'] = THUMBNAIL_FOLDER
# Set ADMIN_PASSWORD in app config for use in blueprints
app.config['ADMIN_PASSWORD'] = os.environ.get('ADMIN_PASSWORD', 'admin')

# --- Utility Functions ---
def create_thumbnail(image_path, thumbnail_path, size=(128, 128)):
    try:
        with Image.open(image_path) as img:
            img.thumbnail(size)
            img.save(thumbnail_path, "PNG")
            return True
    except IOError:
        return False

# --- Database Handling ---
def get_db():
    db_path = app.config['DATABASE']
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found at the expected path: {os.path.abspath(db_path)}")
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = sqlite3.connect(db_path)
        g.sqlite_db.row_factory = sqlite3.Row

        # Apply any necessary schema migrations for new features
        init_db_migrations(g.sqlite_db)

    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

# --- Blueprint Registration ---
# Import the blueprints here to avoid circular imports if they need the app object
from part_lister.routes.admin import admin_bp
from part_lister.routes.scanner import scanner_bp
from part_lister.routes.core import core_bp

app.register_blueprint(admin_bp)
app.register_blueprint(scanner_bp)
app.register_blueprint(core_bp)

# --- Template Compatibility ---
# Context processor to map old `url_for` calls in templates to the new blueprint routes.
@app.context_processor
def override_url_for():
    def custom_url_for(endpoint, **values):
        mapping = {
            'login': 'admin_bp.login',
            'logout': 'admin_bp.logout',
            'admin': 'admin_bp.admin',
            'add_part': 'admin_bp.add_part',
            'edit_part': 'admin_bp.edit_part',
            'part_view': 'admin_bp.part_view',
            'set_thumbnail': 'admin_bp.set_thumbnail',
            'clear_thumbnail': 'admin_bp.clear_thumbnail',
            'delete_attachment': 'admin_bp.delete_attachment',
            'apply_thumbnail': 'admin_bp.apply_thumbnail',
            'select_thumbnail': 'admin_bp.select_thumbnail',
            'bulk_edit': 'admin_bp.bulk_edit',
            'delete_part': 'admin_bp.delete_part',
            'export_parts': 'admin_bp.export_parts',
            'import_parts': 'admin_bp.import_parts',
            'gallery': 'admin_bp.gallery',
            'delete_image': 'admin_bp.delete_image',
            'scanner': 'scanner_bp.scanner',
            'index': 'core_bp.index',
            'add_to_list': 'core_bp.add_to_list',
            'create_list': 'core_bp.create_list',
            'switch_list': 'core_bp.switch_list',
            'api_get_list_items': 'core_bp.api_get_list_items',
            'edit_list_item': 'core_bp.edit_list_item',
            'delete_list_item': 'core_bp.delete_list_item',
            'print_list': 'core_bp.print_list',
            'uploaded_file': 'core_bp.uploaded_file',
            'serve_thumbnail': 'core_bp.serve_thumbnail'
        }
        if endpoint in mapping:
            return original_url_for(mapping[endpoint], **values)
        return original_url_for(endpoint, **values)
    return dict(url_for=custom_url_for)

# --- Main Execution ---
if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['THUMBNAIL_FOLDER'], exist_ok=True)
    app.run(debug=True, host='0.0.0.0')
