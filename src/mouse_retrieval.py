import logging
import os
from typing import Final

# We use 'by-id' because these device names are persistent.
INPUT_DEVICES_PATH: Final = '/dev/input/by-id'

def retrieve_mouse_name() -> str:
    """Attempts to find the connected mouse automatically, or prompts the user to select one."""
    
    # Look through the input directory where persistent device IDs are stored
    all_devices = os.listdir(INPUT_DEVICES_PATH)
    
    # TARGETED FILTER: We only care about devices that have 'event-mouse' in their name.
    # This hides all the keyboards, webcams, and other USB devices from the prompt.
    mouse_devices = list(set([d for d in all_devices if 'event-mouse' in d]))
    n_devices = len(mouse_devices)

    # If no mouse devices are found, abort and tell the user they might need to provide it manually
    if n_devices == 0:
        raise ValueError(f"Couldn't find a mouse ending with 'event-mouse'. Please provide it manually with -m.")

    # If exactly one mouse is found, automatically select it
    if n_devices == 1:
        logging.info(f"Found mouse: {mouse_devices[0]}")
        return mouse_devices[0]

    # If multiple mice are found, present an interactive selection menu in the terminal
    print("Select a mouse device:")
    for idx, device in enumerate(sorted(mouse_devices), start=1):
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
    return mouse_devices[selected_idx - 1]

def abs_mouse_path(device: str) -> str:
    """Combines the folder path and the device name into a full absolute path."""
    return os.path.join(INPUT_DEVICES_PATH, device)
