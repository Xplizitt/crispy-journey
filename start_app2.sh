#!/bin/bash
export PYTHONPATH=.
python3 part_lister/app.py > app.log 2>&1 &
echo $! > app.pid
