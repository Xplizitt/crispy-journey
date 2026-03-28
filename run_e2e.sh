#!/bin/bash
export PYTHONPATH=.
~/.pyenv/versions/3.12.13/bin/python3 part_lister/app.py &
PID=$!
sleep 3
~/.pyenv/versions/3.12.13/bin/python3 -m pytest tests/test_e2e_lists.py
kill $PID
