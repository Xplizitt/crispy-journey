import pytest
import os


@pytest.fixture
def client(tmp_path):
    """Provide a Flask test client with an isolated temporary database."""
    import part_lister.app
    import part_lister.database

    db_path = str(tmp_path / "test.db")
    part_lister.app.app.config['DATABASE'] = db_path
    part_lister.app.app.config['TESTING'] = True

    # Point upload/thumbnail folders to tmp_path so file ops don't pollute the repo
    upload_dir = str(tmp_path / "uploads")
    thumb_dir = str(tmp_path / "thumbnails")
    os.makedirs(upload_dir, exist_ok=True)
    os.makedirs(thumb_dir, exist_ok=True)
    part_lister.app.app.config['UPLOAD_FOLDER'] = upload_dir
    part_lister.app.app.config['THUMBNAIL_FOLDER'] = thumb_dir

    # Initialize a fresh database
    original_db_path = part_lister.database.DATABASE_PATH
    part_lister.database.DATABASE_PATH = db_path

    with part_lister.app.app.app_context():
        part_lister.database.init_db()

    with part_lister.app.app.test_client() as c:
        yield c

    # Restore original path
    part_lister.database.DATABASE_PATH = original_db_path


@pytest.fixture
def auth_client(client):
    """Provide a Flask test client that is already logged in."""
    with client.session_transaction() as sess:
        sess['logged_in'] = True
    return client
