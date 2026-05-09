import logging
from collections import defaultdict
from typing import DefaultDict, Dict, NoReturn, List
import time

import libevdev

def filter_mouse_chattering(evdev: libevdev.Device, threshold: int, buttons_to_filter: List[libevdev.EventCode] = None) -> NoReturn:
    # Small delay to ensure clean startup
    time.sleep(1)
    
    # Grab the mouse device
    evdev.grab()
    
    # Create the virtual uinput mouse
    ui_dev = evdev.create_uinput_device()

    logging.info("Listening to mouse events...")

    if not buttons_to_filter:
        buttons_to_filter = []

    while True:
        for e in evdev.events():
            if _from_click(e, threshold, buttons_to_filter):
                ui_dev.send_events([e, libevdev.InputEvent(libevdev.EV_SYN.SYN_REPORT, 0)])


def _from_click(event: libevdev.InputEvent, threshold: int, buttons_to_filter: List[libevdev.EventCode]) -> bool:
    global _last_btn_code
    
    if event.matches(libevdev.EV_SYN) or event.matches(libevdev.EV_MSC):
        return False

    # CRITICAL MOUSE FIX: Immediately forward all relative (EV_REL) and absolute (EV_ABS) movement.
    # This includes X/Y cursor movement and scroll wheel movement. Do not filter these!
    if event.matches(libevdev.EV_REL) or event.matches(libevdev.EV_ABS):
        return True

    # In Linux, mouse buttons are technically classified as EV_KEY.
    # If it's not a button/key, just forward it.
    if not event.matches(libevdev.EV_KEY):
        return True

    # SPECIFIC BUTTON FILTERING (e.g., BTN_LEFT, BTN_RIGHT)
    if buttons_to_filter and event.code not in buttons_to_filter:
        logging.debug(f'FORWARDING {event.code} (not in targeted filter list)')
        return True

    # Values: 0 for Button Up, 1 for Button Down
    if event.value == 0:
        if _btn_pressed[event.code]:
            logging.debug(f'FORWARDING {event.code} up')
            _last_btn_up[event.code] = event.sec * 1E6 + event.usec
            _btn_pressed[event.code] = False
            return True
        else:
            logging.info(f'FILTERING {event.code} up: button not pressed beforehand')
            return False

    prev = _last_btn_up.get(event.code)
    now = event.sec * 1E6 + event.usec

    # Check against the last button pressed so alternating clicks (Left -> Right -> Left) don't get filtered
    if prev is None or now - prev > threshold * 1E3 or _last_btn_code != event.code:
        logging.debug(f'FORWARDING {event.code} down')
        _btn_pressed[event.code] = True
        _last_btn_code = event.code
        return True

    logging.info(f'FILTERED {event.code} down: last button up event happened {(now - prev) / 1E3} ms ago')
    return False

_last_btn_up: Dict[libevdev.EventCode, int] = {}
_btn_pressed: DefaultDict[libevdev.EventCode, bool] = defaultdict(bool)
_last_btn_code = None
