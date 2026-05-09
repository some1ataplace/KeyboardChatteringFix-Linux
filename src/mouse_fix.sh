#!/bin/bash
# Change the line below to the absolute path of the folder
# You can append `--buttons BTN_LEFT,BTN_SIDE` at the very end to ONLY filter those specific buttons.

cd <absolute/path/to/folder> && sudo python3 mouse_main.py -m <MOUSE id> -t <OPTIONAL, 30 is the default threshold>
