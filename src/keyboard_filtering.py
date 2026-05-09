import logging
from collections import defaultdict
from typing import DefaultDict, Dict, NoReturn, List
import time

import libevdev


def filter_chattering(evdev: libevdev.Device, threshold: int, keys_to_filter: List[libevdev.EventCode] = None) -> NoReturn:
    time.sleep(1) # Delay to allow Enter key to release natively
    evdev.grab()
    ui_dev = evdev.create_uinput_device()

    logging.info("Listening to keyboard input events...")

    if not keys_to_filter:
        keys_to_filter = []

    while True:
        for e in evdev.events():
            if _from_keystroke(e, threshold, keys_to_filter):
                ui_dev.send_events([e, libevdev.InputEvent(libevdev.EV_SYN.SYN_REPORT, 0)])


def _from_keystroke(event: libevdev.InputEvent, threshold: int, keys_to_filter: List[libevdev.EventCode]) -> bool:
    global _last_key_code
    
    if event.matches(libevdev.EV_SYN) or event.matches(libevdev.EV_MSC):
        return False

    # Do not filter modifier combinations or held keys
    if not event.matches(libevdev.EV_KEY) or event.value > 1:
        logging.debug(f'FORWARDING {event.code}')
        return True

    # SPECIFIC KEY FILTERING
    if keys_to_filter and event.code not in keys_to_filter:
        logging.debug(f'FORWARDING {event.code} (not in targeted filter list)')
        return True

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

    # Check _last_key_code to prevent filtering fast alternating letters (e.g., e -> v -> e)
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
