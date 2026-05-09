import logging
from collections import defaultdict
from typing import DefaultDict, Dict, NoReturn, List
import time
import libevdev


def filter_chattering(evdev: libevdev.Device, threshold: int, keys_to_filter: List[libevdev.EventCode] = None) -> NoReturn:
    # Delay to allow the Enter key (used to execute the terminal command) 
    # to release natively before we grab the device. Prevents a "stuck" Enter key.
    time.sleep(1) 
    
    # Grab the physical device so only we see the events it emits
    evdev.grab()
    
    # Create a virtual uinput device to emit our cleaned events back to the OS
    ui_dev = evdev.create_uinput_device()

    logging.info("Listening to keyboard input events...")

    if not keys_to_filter:
        keys_to_filter = []

    while True:
        # Descriptor is blocking; waits until physical events are available
        try:
            for e in evdev.events():
                if _from_keystroke(e, threshold, keys_to_filter):
                    ui_dev.send_events([e, libevdev.InputEvent(libevdev.EV_SYN.SYN_REPORT, 0)])
        except OSError as err:
            # Errno 19 means "No such device". This happens if the USB is suddenly unplugged.
            if err.errno == 19:
                logging.critical("Keyboard disconnected while listening. Exiting gracefully.")
                sys.exit(0)
            else:
                raise err


def _from_keystroke(event: libevdev.InputEvent, threshold: int, keys_to_filter: List[libevdev.EventCode]) -> bool:
    global _last_key_code
    
    # Ignore sync/misc events. libevdev uinput handles syncing natively.
    if event.matches(libevdev.EV_SYN) or event.matches(libevdev.EV_MSC):
        return False

    # MODIFIER FIX: If the event isn't a key, or it's a "hold" event (event.value > 1), forward it immediately.
    # This ensures held keys (like Shift or Ctrl) don't get interrupted by the chatter filter.
    if not event.matches(libevdev.EV_KEY) or event.value > 1:
        logging.debug(f'FORWARDING {event.code}')
        return True

    # TARGETED FILTERING: If the user provided specific keys to fix, and this isn't one of them, forward it.
    if keys_to_filter and event.code not in keys_to_filter:
        logging.debug(f'FORWARDING {event.code} (not in targeted filter list)')
        return True

    # Process standard Key Up (0) and Key Down (1) events
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

    # DOUBLE-LETTER FIX: Check `_last_key_code != event.code`.
    # If a user types fast alternating letters (e.g. e -> v -> e), the second 'e' won't be 
    # mistakenly filtered, because the 'v' reset the _last_key_code.
    if prev is None or now - prev > threshold * 1E3 or _last_key_code != event.code:
        logging.debug(f'FORWARDING {event.code} down')
        _key_pressed[event.code] = True
        _last_key_code = event.code
        return True

    logging.info(f'FILTERED {event.code} down: last key up event happened {(now - prev) / 1E3} ms ago')
    return False

# Global state trackers
_last_key_up: Dict[libevdev.EventCode, int] = {}
_key_pressed: DefaultDict[libevdev.EventCode, bool] = defaultdict(bool)
_last_key_code = None
