import subprocess
import time

server = subprocess.Popen(['python3', 'part_lister/app.py'], env={'PYTHONPATH': '.'})
time.sleep(3)

try:
    subprocess.run(['python3', '-m', 'pytest', 'tests/test_e2e_lists.py'], env={'PYTHONPATH': '.'})
finally:
    server.terminate()
