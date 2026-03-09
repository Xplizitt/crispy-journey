import subprocess
import sys
import os
import tempfile
import time
import urllib.request
import urllib.error


def wait_for_server(url, timeout=15):
    """Poll the server until it responds or timeout is reached."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(url, timeout=2)
            return True
        except (urllib.error.URLError, ConnectionError, OSError):
            time.sleep(0.5)
    return False


def main():
    # Use a temporary database for E2E tests
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, 'e2e_test.db')

        env = os.environ.copy()
        env['PYTHONPATH'] = '.'
        env['E2E_DATABASE_PATH'] = db_path

        # Initialize the database
        subprocess.run(
            [sys.executable, 'part_lister/database.py'],
            env={**env, 'DATABASE_PATH': db_path},
            check=True,
        )

        # Start server
        server = subprocess.Popen(
            [sys.executable, 'part_lister/app.py'],
            env=env,
        )

        try:
            if not wait_for_server('http://127.0.0.1:5000/', timeout=15):
                print('ERROR: Server did not start within 15 seconds', file=sys.stderr)
                sys.exit(1)

            result = subprocess.run(
                [sys.executable, '-m', 'pytest', '-m', 'e2e', 'tests/', '-v'],
                env=env,
            )
            sys.exit(result.returncode)
        finally:
            server.terminate()
            server.wait(timeout=5)


if __name__ == '__main__':
    main()
