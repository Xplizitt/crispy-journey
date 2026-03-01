import sqlite3
import os
from PIL import Image

_basedir = os.path.abspath(os.path.dirname(__file__))
# the db file is actually one level up based on your path finding
DATABASE_PATH = os.path.join(_basedir, 'parts.db')
UPLOAD_FOLDER = os.path.join(_basedir, 'part_lister', 'static', 'uploads')
THUMBNAIL_FOLDER = os.path.join(_basedir, 'part_lister', 'static', 'thumbnails')

def create_thumbnail(image_path, thumbnail_path, size=(128, 128)):
    try:
        with Image.open(image_path) as img:
            img.thumbnail(size)
            img.save(thumbnail_path, "PNG")
            return True
    except IOError as e:
        print(f"Error creating thumbnail for {image_path}: {e}")
        return False

def generate_all_thumbnails():
    os.makedirs(THUMBNAIL_FOLDER, exist_ok=True)

    # We need to initialize the db
    if os.path.exists(DATABASE_PATH) and os.path.getsize(DATABASE_PATH) == 0:
        os.remove(DATABASE_PATH)

    if not os.path.exists(DATABASE_PATH):
        print("Database not found. Initialize it first.")
        from part_lister.database import init_db
        init_db()

    db = sqlite3.connect(DATABASE_PATH)
    db.row_factory = sqlite3.Row
    cur = db.cursor()

    cur.execute('''
        SELECT id, filename FROM attachments
        WHERE filename LIKE '%.jpg' OR filename LIKE '%.jpeg' OR filename LIKE '%.png' OR filename LIKE '%.gif'
    ''')
    images = cur.fetchall()

    for image in images:
        filename = image['filename']
        original_path = os.path.join(UPLOAD_FOLDER, filename)
        # Generate thumbnail with prefix thumb_gallery_
        thumb_filename = f"thumb_gallery_{filename}"
        thumb_path = os.path.join(THUMBNAIL_FOLDER, thumb_filename)

        if not os.path.exists(thumb_path) and os.path.exists(original_path):
            print(f"Generating thumbnail for {filename}...")
            create_thumbnail(original_path, thumb_path)

    db.close()
    print("Thumbnail generation complete.")

if __name__ == "__main__":
    generate_all_thumbnails()
