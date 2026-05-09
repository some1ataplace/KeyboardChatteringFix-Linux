import logging
import os
from typing import Final

# We use the 'by-id' folder because the device names here are persistent.
# If we used the standard '/dev/input/eventX', the numbers might change every time you reboot or plug in a USB.
INPUT_DEVICES_PATH: Final = '/dev/input/by-id'


def retrieve_keyboard_name() -> str:
    """
    Lists all devices in the input directory and prompts the user to select one.
    This is triggered when the script is run without the `-k` argument.
    """

    # Filter to ONLY show valid modern event nodes. This safely hides legacy raw nodes (like '-mouse' or '-kbd') which would crash libevdev, but keeps all virtual '-event-kbd' and '-event-mouse' nodes visible.
    #valid_devices = [d for d in all_devices if '-event-' in d]
    #device_list = list(set(valid_devices))
    #n_devices = len(device_list)
    
    # Read the directory to get a list of all connected input devices
    all_devices = os.listdir(INPUT_DEVICES_PATH)
    
    # Deduplicate the list natively using a set to ensure clean output
    keyboard_devices = list(set(all_devices))
    n_devices = len(keyboard_devices)

    # If no devices are found in the folder at all, abort the script
    if n_devices == 0:
        raise ValueError(f"Couldn't find any devices in '{INPUT_DEVICES_PATH}'")

    # Present an interactive selection menu in the terminal.
    # We list EVERYTHING because modern gaming keyboards and mice often register as multiple 
    # virtual devices (e.g. separate endpoints for macro keys, RGB controllers, etc).
    print("Select a keyboard device:")
    
    # Sort the devices alphabetically so they are easy to read
    for idx, device in enumerate(sorted(keyboard_devices), start=1):
        print(f"{idx}. {device}")

    selected_idx = -1
    
    # Loop continuously until the user inputs a valid number corresponding to the list
    while selected_idx < 1 or selected_idx > n_devices:
        try:
            # Capture keyboard input from the user
            selected_idx = int(input("Enter your choice (number): "))
            
            # Warn the user if they pick a number outside the valid range
            if selected_idx < 1 or selected_idx > n_devices:
                print(f"Please select a number between 1 and {n_devices}")
                
        except ValueError:
            # Warn the user if they type letters instead of numbers
            print("Please enter a valid number")

    # Return the string name of the selected device.
    # We subtract 1 because our visual list started at 1, but Python arrays start at 0.
    # We also must sort the list here identically to how we printed it, so the index matches.
    sorted_devices = sorted(keyboard_devices)
    return sorted_devices[selected_idx - 1]


def abs_keyboard_path(device: str) -> str:
    """
    Helper function that combines the folder path and the device name 
    into a full absolute path (e.g., /dev/input/by-id/usb-keyboard-name)
    """
    return os.path.join(INPUT_DEVICES_PATH, device)
