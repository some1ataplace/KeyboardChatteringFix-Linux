import argparse
import logging
import sys
import os
from contextlib import contextmanager

import libevdev

from src.filtering import filter_chattering
from src.keyboard_retrieval import retrieve_keyboard_name, INPUT_DEVICES_PATH, abs_keyboard_path

# Import the config file. If missing/broken, default to empty safely.
try:
    from src.config import FILTERED_KEYS
except ImportError:
    FILTERED_KEYS = set()


@contextmanager
def get_device_handle(keyboard_name: str) -> libevdev.Device:
    """ Safely get an evdev device handle. """
    device_path = abs_keyboard_path(keyboard_name)
    
    # If the physical keyboard is disconnected/undocked, the script 
    # used to crash and loop at 100% CPU. Now, it checks if the path exists. 
    # If not, it cleanly exits (status 0). Systemd will try to restart it later safely.
    if not os.path.exists(device_path):
        logging.critical(f"Keyboard device {keyboard_name} not connected. Exiting to prevent CPU loop.")
        sys.exit(0)

    fd = open(device_path, 'rb')
    evdev = libevdev.Device(fd)
    try:
        yield evdev
    finally:
        fd.close()


def parse_keys(keys_str):
    """Parse a comma-separated list of keys into a list of strings."""
    if not keys_str:
        return []
    return [key.strip() for key in keys_str.split(',')]
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', '--keyboard', type=str, default=str(),
                        help=f"Name of your chattering keyboard device as listed in {INPUT_DEVICES_PATH}. "
                             f"If left unset, will be attempted to be retrieved automatically.")
    parser.add_argument('-t', '--threshold', type=int, default=30, help="Filter time threshold in milliseconds. "
                                                                        "Default=30ms.")
    parser.add_argument('--keys', type=parse_keys, default=[], help="Comma-separated list of keys to filter. Default All. e.g KEY_A,KEY_SPACE")
    parser.add_argument('-v', '--verbosity', type=int, default=1, choices=[0, 1, 2])
    args = parser.parse_args()

    logging.basicConfig(
        level={
            0: logging.CRITICAL,
            1: logging.INFO,
            2: logging.DEBUG
        }[args.verbosity],
        handlers=[
            logging.StreamHandler(sys.stdout)
        ],
        format="%(asctime)s - %(message)s",
        datefmt="%H:%M:%S"
    )

    # PRECEDENCE LOGIC FOR TARGETED KEYS:
    # 1. Use --keys argument if provided.
    # 2. Use src/config.py if no argument is provided.
    # 3. If both are empty, list stays empty (Filter ALL keys natively).
    keys_list = []
    if args.keys:
        logging.info("Using targeted keys from command line argument --keys")
        keys_list = args.keys
    elif FILTERED_KEYS:
        logging.info("Using targeted keys from src/config.py")
        keys_list = list(FILTERED_KEYS)
    else:
        logging.info("No specific keys targeted. Filtering ALL keys.")

    # Convert requested string keys to libevdev.EventCode objects
    keys_to_filter = []
    for key in keys_list:
        try:
            keys_to_filter.append(libevdev.evbit(key))
        except Exception as e:
            logging.warning(f"Key '{key}' not recognized by libevdev and will be ignored. Error: {e}")

    with get_device_handle(args.keyboard or retrieve_keyboard_name()) as device:
        filter_chattering(device, args.threshold, keys_to_filter)
