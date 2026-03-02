import subprocess
import time

process = subprocess.Popen(["python3", "part_lister/app.py"])
time.sleep(2) # wait for app to start
