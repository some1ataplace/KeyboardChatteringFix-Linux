import logging
import os
from typing import Final

INPUT_DEVICES_PATH: Final = '/dev/input/by-id'

def retrieve_mouse_name() -> str:
    all_devices = os.listdir(INPUT_DEVICES_PATH)
    
    # Filter only for mouse devices
    mouse_devices = list(set([d for d in all_devices if 'event-mouse' in d]))
    n_devices = len(mouse_devices)

    if n_devices == 0:
        raise ValueError(f"Couldn't find a mouse ending with 'event-mouse' in '{INPUT_DEVICES_PATH}'. You may need to provide it manually using -m.")

    if n_devices == 1:
        logging.info(f"Found mouse: {mouse_devices[0]}")
        return mouse_devices[0]

    print("Select a mouse device:")
    for idx, device in enumerate(sorted(mouse_devices), start=1):
        print(f"{idx}. {device}")

    selected_idx = -1
    while selected_idx < 1 or selected_idx > n_devices:
        try:
            selected_idx = int(input("Enter your choice (number): "))
            if selected_idx < 1 or selected_idx > n_devices:
                print(f"Please select a number between 1 and {n_devices}")
        except ValueError:
            print("Please enter a valid number")

    return mouse_devices[selected_idx - 1]

def abs_mouse_path(device: str) -> str:
    return os.path.join(INPUT_DEVICES_PATH, device)
