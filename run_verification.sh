#!/bin/bash
export PYTHONPATH=.
~/.pyenv/versions/3.12.12/bin/python3 part_lister/app.py &
PID=$!
sleep 3
~/.pyenv/versions/3.12.12/bin/python3 /home/jules/verification/verify_customers.py
kill $PID
