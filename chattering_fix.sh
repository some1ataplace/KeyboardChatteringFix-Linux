#!/bin/bash
# Change the line below to the absolute path of the folder
# You can append `--keys KEY_A,KEY_SPACE` at the very end to ONLY filter those specific keys.
# (If using modern Python, you may need to run: sudo pip3 install -r requirements.txt --break-system-packages)

cd <absolute/path/to/folder> && sudo python3 -m src -k <KEYBOARD id> -t <OPTIONAL, 30 is the default threshold>
