import argparse
import logging
import sys
import os
from contextlib import contextmanager
import libevdev

from src.keyboard_filtering import filter_chattering
from src.keyboard_retrieval import retrieve_keyboard_name, INPUT_DEVICES_PATH, abs_keyboard_path

try:
    from src.keyboard_config import FILTERED_KEYS
except ImportError:
    FILTERED_KEYS = set()

@contextmanager
def get_device_handle(keyboard_name: str) -> libevdev.Device:
    device_path = abs_keyboard_path(keyboard_name)
    if not os.path.exists(device_path):
        logging.critical(f"Keyboard {keyboard_name} not connected. Exiting to prevent CPU loop.")
        sys.exit(0)

    fd = open(device_path, 'rb')
    evdev = libevdev.Device(fd)
    try:
        yield evdev
    finally:
        fd.close()

def parse_keys(keys_str):
    if not keys_str: return []
    return [key.strip() for key in keys_str.split(',')]
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', '--keyboard', type=str, default=str())
    parser.add_argument('-t', '--threshold', type=int, default=30)
    parser.add_argument('--keys', type=parse_keys, default=[])
    parser.add_argument('-v', '--verbosity', type=int, default=1, choices=[0, 1, 2])
    args = parser.parse_args()

    logging.basicConfig(level={0: logging.CRITICAL, 1: logging.INFO, 2: logging.DEBUG}[args.verbosity],
                        handlers=[logging.StreamHandler(sys.stdout)],
                        format="%(asctime)s - %(message)s", datefmt="%H:%M:%S")

    keys_list = args.keys if args.keys else list(FILTERED_KEYS)
    keys_to_filter = []
    
    for key in keys_list:
        try:
            keys_to_filter.append(libevdev.evbit(key))
        except Exception as e:
            logging.warning(f"Key '{key}' ignored: {e}")

    with get_device_handle(args.keyboard or retrieve_keyboard_name()) as device:
        filter_chattering(device, args.threshold, keys_to_filter)
