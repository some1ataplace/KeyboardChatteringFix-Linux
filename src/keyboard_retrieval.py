import logging
import os
from typing import Final

# We use 'by-id' because these device names are persistent. 
# If we used standard '/dev/input/eventX', the ID might change every time you reboot or plug in a USB.
INPUT_DEVICES_PATH: Final = '/dev/input/by-id'

def retrieve_keyboard_name() -> str:
    """Attempts to find the connected keyboard automatically, or prompts the user to select one."""
    
    # Look through the input directory where persistent device IDs are stored
    all_devices = os.listdir(INPUT_DEVICES_PATH)
    
    # Deduplicate the list natively using a set
    keyboard_devices = list(set(all_devices))
    n_devices = len(keyboard_devices)

    # If no devices are found in the folder at all, abort
    if n_devices == 0:
        raise ValueError(f"Couldn't find a keyboard in '{INPUT_DEVICES_PATH}'")

    # If exactly one device is found, automatically select it without bothering the user
    if n_devices == 1:
        logging.info(f"Found keyboard: {keyboard_devices[0]}")
        return keyboard_devices[0]

    # If multiple devices are found, present an interactive selection menu in the terminal
    print("Select a keyboard device:")
    for idx, device in enumerate(sorted(keyboard_devices), start=1):
        print(f"{idx}. {device}")

    selected_idx = -1
    
    # Loop until the user inputs a valid number corresponding to the list
    while selected_idx < 1 or selected_idx > n_devices:
        try:
            selected_idx = int(input("Enter your choice (number): "))
            if selected_idx < 1 or selected_idx > n_devices:
                print(f"Please select a number between 1 and {n_devices}")
        except ValueError:
            print("Please enter a valid number")

    # Return the string name of the selected device (subtracting 1 because arrays are 0-indexed)
    return keyboard_devices[selected_idx - 1]

def abs_keyboard_path(device: str) -> str:
    """Combines the folder path and the device name into a full absolute path."""
    return os.path.join(INPUT_DEVICES_PATH, device)
