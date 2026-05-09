import logging
from collections import defaultdict
from typing import DefaultDict, Dict, NoReturn, List
import time
import libevdev
import sys

def filter_mouse_chattering(evdev: libevdev.Device, threshold: int, buttons_to_filter: List[libevdev.EventCode] = None) -> NoReturn:
    time.sleep(1) # Delay for clean startup
    evdev.grab()
    ui_dev = evdev.create_uinput_device()

    logging.info("Listening to mouse events...")

    if not buttons_to_filter:
        buttons_to_filter = []

    while True:
        try:
            for e in evdev.events():
                if _from_click(e, threshold, buttons_to_filter):
                    ui_dev.send_events([e, libevdev.InputEvent(libevdev.EV_SYN.SYN_REPORT, 0)])
        except OSError as err:
            # Errno 19 means "No such device". This happens if the USB is suddenly unplugged.
            if err.errno == 19:
                logging.critical("Mouse disconnected while listening. Exiting gracefully.")
                sys.exit(0)
            else:
                raise err

def _from_click(event: libevdev.InputEvent, threshold: int, buttons_to_filter: List[libevdev.EventCode]) -> bool:
    global _last_btn_code
    
    if event.matches(libevdev.EV_SYN) or event.matches(libevdev.EV_MSC):
        return False

    # CRITICAL MOUSE FIX: Immediately forward all movement data.
    # EV_REL = Relative movement (standard X/Y cursor movement and scroll wheel)
    # EV_ABS = Absolute movement (drawing tablets, touchpads)
    # Skipping this prevents the cursor from freezing or stuttering.
    if event.matches(libevdev.EV_REL) or event.matches(libevdev.EV_ABS):
        return True

    # In Linux, mouse clicks are classified as EV_KEY. 
    # If it isn't an EV_KEY, or it's a natively held click (value > 1), forward it.
    if not event.matches(libevdev.EV_KEY) or event.value > 1:
        return True

    # TARGETED FILTERING: If the user provided specific buttons to fix, forward everything else.
    if buttons_to_filter and event.code not in buttons_to_filter:
        return True

    # Process Button Up (0) and Button Down (1)
    if event.value == 0:
        if _btn_pressed[event.code]:
            _last_btn_up[event.code] = event.sec * 1E6 + event.usec
            _btn_pressed[event.code] = False
            return True
        else:
            return False

    prev = _last_btn_up.get(event.code)
    now = event.sec * 1E6 + event.usec

    # Check _last_btn_code to allow fast alternating clicks (e.g. Left -> Right -> Left)
    if prev is None or now - prev > threshold * 1E3 or _last_btn_code != event.code:
        _btn_pressed[event.code] = True
        _last_btn_code = event.code
        return True

    logging.info(f'FILTERED {event.code} down: last up event {(now - prev) / 1E3} ms ago')
    return False

# Global state trackers
_last_btn_up: Dict[libevdev.EventCode, int] = {}
_btn_pressed: DefaultDict[libevdev.EventCode, bool] = defaultdict(bool)
_last_btn_code = None
