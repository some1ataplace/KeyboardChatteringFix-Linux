#!/bin/bash
# Change the line below to the absolute path of the folder.
# You can append `--buttons BTN_LEFT,BTN_SIDE` at the very end to ONLY filter those specific buttons.
# (If using modern Linux/Python, you may need to run: sudo pip3 install -r requirements.txt --break-system-packages)

cd </absolute/path/to/folder> && sudo python3 -m src.mouse_main -m <MOUSE id> -t 30
