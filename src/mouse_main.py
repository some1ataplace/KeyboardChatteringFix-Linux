import argparse
import logging
import sys
import os
from contextlib import contextmanager
import libevdev

from src.mouse_filtering import filter_mouse_chattering
from src.mouse_retrieval import retrieve_mouse_name, INPUT_DEVICES_PATH, abs_mouse_path

# Safely import the config file if it exists
try:
    from src.mouse_config import FILTERED_BUTTONS
except ImportError:
    FILTERED_BUTTONS = set()

@contextmanager
def get_device_handle(mouse_name: str) -> libevdev.Device:
    device_path = abs_mouse_path(mouse_name)
    
    # DISCONNECT FIX: Prevent 100% CPU exhaustion loop if mouse is turned off/unplugged.
    if not os.path.exists(device_path):
        logging.critical(f"Mouse {mouse_name} not connected. Exiting to prevent CPU loop.")
        sys.exit(0)

    fd = open(device_path, 'rb')
    evdev = libevdev.Device(fd)
    try:
        yield evdev
    finally:
        fd.close()

def parse_buttons(buttons_str):
    """Parses comma-separated CLI arguments into a list of strings."""
    if not buttons_str: return []
    return [btn.strip() for btn in buttons_str.split(',')]
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mouse', type=str, default=str())
    parser.add_argument('-t', '--threshold', type=int, default=30)
    parser.add_argument('--buttons', type=parse_buttons, default=[])
    parser.add_argument('-v', '--verbosity', type=int, default=1, choices=[0, 1, 2])
    args = parser.parse_args()

    logging.basicConfig(level={0: logging.CRITICAL, 1: logging.INFO, 2: logging.DEBUG}[args.verbosity],
                        handlers=[logging.StreamHandler(sys.stdout)],
                        format="%(asctime)s - %(message)s", datefmt="%H:%M:%S")

    # CONFIG PRECEDENCE: CLI args > mouse_config.py > Empty (Filter All)
    buttons_list = args.buttons if args.buttons else list(FILTERED_BUTTONS)
    buttons_to_filter = []
    
    # Convert string button names (e.g., "BTN_LEFT") to libevdev.EventCode objects
    for btn in buttons_list:
        try:
            buttons_to_filter.append(libevdev.evbit(btn))
        except Exception as e:
            logging.warning(f"Button '{btn}' ignored: {e}")

    with get_device_handle(args.mouse or retrieve_mouse_name()) as device:
        filter_mouse_chattering(device, args.threshold, buttons_to_filter)
