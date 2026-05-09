import logging
from collections import defaultdict
from typing import DefaultDict, Dict, NoReturn, List
import time

import libevdev
import time

def filter_chattering(evdev: libevdev.Device, threshold: int, keys_to_filter: List[libevdev.EventCode] = None) -> NoReturn:
    # Add delay to allow the Enter key to release after executing the script via terminal
    time.sleep(1)
    
    # Grab the device - now only we see the events it emits
    evdev.grab()
    
    # Create a virtual uinput device - this will emit the filtered events to the OS
    ui_dev = evdev.create_uinput_device()

    logging.info("Listening to input events...")

    if not keys_to_filter:
        keys_to_filter = []

    while True:
        # Descriptor is blocking; this waits until events are available
        for e in evdev.events():
            if _from_keystroke(e, threshold, keys_to_filter):
                ui_dev.send_events([e, libevdev.InputEvent(libevdev.EV_SYN.SYN_REPORT, 0)])


def _from_keystroke(event: libevdev.InputEvent, threshold: int, keys_to_filter: List[libevdev.EventCode]) -> bool:
    global _last_key_code
    
    # No need to relay sync/misc events - libevdev uinput handles syncing
    if event.matches(libevdev.EV_SYN) or event.matches(libevdev.EV_MSC):
        return False

    # Fix for Modifiers/Combinations: If the event isn't a key, or it's a "hold" event (value > 1), forward it.
    # Holding a key naturally spams events; we don't want to filter those.
    if not event.matches(libevdev.EV_KEY) or event.value > 1:
        logging.debug(f'FORWARDING {event.code}')
        return True

    # SPECIFIC KEY FILTERING: If the user provided specific keys to fix, and this isn't one of them, forward it.
    if keys_to_filter and event.code not in keys_to_filter:
        logging.debug(f'FORWARDING {event.code} (not in targeted filter list)')
        return True

    # Values: 0 for Key Up, 1 for Key Down, 2 for Key Hold
    if event.value == 0:
        if _key_pressed[event.code]:
            logging.debug(f'FORWARDING {event.code} up')
            _last_key_up[event.code] = event.sec * 1E6 + event.usec
            _key_pressed[event.code] = False
            return True
        else:
            logging.info(f'FILTERING {event.code} up: key not pressed beforehand')
            return False

    prev = _last_key_up.get(event.code)
    now = event.sec * 1E6 + event.usec

    # We now check `_last_key_code != event.code`. 
    # If you type fast (e.g. e -> v -> e), the second 'e' won't be filtered just because it was fast, 
    # because 'v' was pressed in between!
    if prev is None or now - prev > threshold * 1E3 or _last_key_code != event.code:
        logging.debug(f'FORWARDING {event.code} down')
        _key_pressed[event.code] = True
        _last_key_code = event.code
        return True

    logging.info(f'FILTERED {event.code} down: last key up event happened {(now - prev) / 1E3} ms ago')
    return False


_last_key_up: Dict[libevdev.EventCode, int] = {}
_key_pressed: DefaultDict[libevdev.EventCode, bool] = defaultdict(bool)
_last_key_code = None
