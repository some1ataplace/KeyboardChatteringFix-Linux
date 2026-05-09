#!/bin/bash
# Change the line below to the absolute path of the folder
# You can append `--buttons BTN_LEFT,BTN_SIDE` at the very end to ONLY filter those specific buttons.

cd </absolute/path/to/folder> && sudo python3 -m src.mouse_main -m <MOUSE id> -t 30
