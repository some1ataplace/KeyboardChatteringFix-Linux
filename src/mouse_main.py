import argparse
import logging
import sys
import os
from contextlib import contextmanager

import libevdev

from src.mouse_filtering import filter_mouse_chattering
from src.mouse_retrieval import retrieve_mouse_name, INPUT_DEVICES_PATH, abs_mouse_path

# Import the config file. If missing/broken, default to empty safely.
try:
    from src.mouse_config import FILTERED_BUTTONS
except ImportError:
    FILTERED_BUTTONS = set()

@contextmanager
def get_device_handle(mouse_name: str) -> libevdev.Device:
    device_path = abs_mouse_path(mouse_name)
    
    if not os.path.exists(device_path):
        logging.critical(f"Mouse device {mouse_name} not connected. Exiting to prevent CPU loop.")
        sys.exit(0)

    fd = open(device_path, 'rb')
    evdev = libevdev.Device(fd)
    try:
        yield evdev
    finally:
        fd.close()

def parse_buttons(buttons_str):
    if not buttons_str:
        return []
    return [btn.strip() for btn in buttons_str.split(',')]
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mouse', type=str, default=str(),
                        help=f"Name of your chattering mouse device as listed in {INPUT_DEVICES_PATH}.")
    parser.add_argument('-t', '--threshold', type=int, default=30, help="Filter time threshold in milliseconds. Default=30ms.")
    parser.add_argument('--buttons', type=parse_buttons, default=[], help="Comma-separated list of buttons to filter. e.g BTN_LEFT,BTN_RIGHT")
    parser.add_argument('-v', '--verbosity', type=int, default=1, choices=[0, 1, 2])
    args = parser.parse_args()

    logging.basicConfig(level={0: logging.CRITICAL, 1: logging.INFO, 2: logging.DEBUG}[args.verbosity],
                        handlers=[logging.StreamHandler(sys.stdout)],
                        format="%(asctime)s - %(message)s", datefmt="%H:%M:%S")

    # PRECEDENCE LOGIC FOR TARGETED BUTTONS:
    buttons_list = []
    if args.buttons:
        logging.info("Using targeted buttons from command line argument --buttons")
        buttons_list = args.buttons
    elif FILTERED_BUTTONS:
        logging.info("Using targeted buttons from src/mouse_config.py")
        buttons_list = list(FILTERED_BUTTONS)
    else:
        logging.info("No specific buttons targeted. Filtering ALL buttons.")

    buttons_to_filter = []
    for btn in buttons_list:
        try:
            buttons_to_filter.append(libevdev.evbit(btn))
        except Exception as e:
            logging.warning(f"Button '{btn}' not recognized by libevdev and will be ignored. Error: {e}")

    with get_device_handle(args.mouse or retrieve_mouse_name()) as device:
        filter_mouse_chattering(device, args.threshold, buttons_to_filter)
