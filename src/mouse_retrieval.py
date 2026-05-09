import logging
import os
from typing import Final

# We use the 'by-id' folder because the device names here are persistent.
INPUT_DEVICES_PATH: Final = '/dev/input/by-id'


def retrieve_mouse_name() -> str:
    """
    Lists all devices in the input directory and prompts the user to select one.
    This is triggered when the script is run without the `-m` argument.
    """
    
    # Read the directory to get a list of all connected input devices
    all_devices = os.listdir(INPUT_DEVICES_PATH)
    
    # We intentionally do NOT filter for the word 'mouse' here. 
    # Advanced gaming mice (like Razer or Logitech) often split their buttons into virtual 
    # keyboard endpoints (e.g. '-if01-event-kbd'). Showing all devices ensures you can find it.
    mouse_devices = list(set(all_devices))
    n_devices = len(mouse_devices)

    # If no devices are found, abort and tell the user they might need to provide it manually
    if n_devices == 0:
        raise ValueError(f"Couldn't find any devices in '{INPUT_DEVICES_PATH}'. Please provide it manually with -m.")

    # Present an interactive selection menu in the terminal.
    print("Select a mouse device:")
    
    # Sort the devices alphabetically so they are easy to read
    for idx, device in enumerate(sorted(mouse_devices), start=1):
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
    sorted_devices = sorted(mouse_devices)
    return sorted_devices[selected_idx - 1]


def abs_mouse_path(device: str) -> str:
    """
    Helper function that combines the folder path and the device name 
    into a full absolute path (e.g., /dev/input/by-id/usb-mouse-name)
    """
    return os.path.join(INPUT_DEVICES_PATH, device)
