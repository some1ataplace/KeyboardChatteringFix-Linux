import re
from pathlib import Path
from typing import Final

INPUT_DEVICES_PATH: Final = Path("/dev/input/by-id")
RAW_INPUT_DEVICES_PATH: Final = Path("/dev/input")
SYSFS_INPUT_DEVICES_PATH: Final = Path("/sys/class/input")
RAW_EVENT_NAME_PATTERN: Final = re.compile(r"event\d+")


def _list_input_devices() -> list[Path]:
    try:
        by_id_devices = [
            path for path in INPUT_DEVICES_PATH.iterdir() if "-event-" in path.name
        ]
    except FileNotFoundError:
        by_id_devices = []

    if by_id_devices:
        return sorted(by_id_devices)

    try:
        raw_devices = [
            path
            for path in RAW_INPUT_DEVICES_PATH.iterdir()
            if RAW_EVENT_NAME_PATTERN.fullmatch(path.name)
        ]
        return sorted(raw_devices, key=lambda path: int(path.name[5:]))
    except FileNotFoundError:
        return []


def retrieve_input_device_name(device_type: str) -> str:
    """List input event devices and prompt the user to select one."""
    device_paths = _list_input_devices()
    if not device_paths:
        raise ValueError(
            "Couldn't find any input event devices under "
            f"'{INPUT_DEVICES_PATH}' or '{RAW_INPUT_DEVICES_PATH}'. "
            "Check that the input devices are available, or pass a device path "
            "explicitly."
        )

    all_devices = [(path, _describe_device(path)) for path in device_paths]
    likely_devices = _likely_device_options(all_devices, device_type)
    device_options = likely_devices or all_devices
    show_all_option = bool(likely_devices and len(likely_devices) < len(all_devices))
    if likely_devices:
        list_title = f"Likely {device_type} devices:"
    else:
        list_title = f"No likely {device_type} names found; showing all event devices:"

    while True:
        print(list_title)
        for index, (_, label) in enumerate(device_options, start=1):
            print(f"{index}. {label}")
        if show_all_option:
            print("0. Show all input event devices")

        try:
            selected_index = int(input("Enter your choice (number): "))
        except ValueError:
            print("Please enter a valid number")
            continue

        if selected_index == 0 and show_all_option:
            device_options = all_devices
            show_all_option = False
            list_title = "All input event devices:"
            continue

        if 1 <= selected_index <= len(device_options):
            selected_path = device_options[selected_index - 1][0]
            if selected_path.parent == INPUT_DEVICES_PATH:
                return selected_path.name
            return str(selected_path)

        print(f"Please select a number between 1 and {len(device_options)}")


def _likely_device_options(
    devices: list[tuple[Path, str]], device_type: str
) -> list[tuple[Path, str]]:
    if device_type == "keyboard":
        matches = [
            device
            for device in devices
            if any(
                marker in device[1].casefold()
                for marker in ("keyboard", "keypad", "event-kbd")
            )
        ]
        return _sort_physical_devices_first(matches)

    if device_type == "mouse":
        mouse_devices = [
            device for device in devices if "mouse" in device[1].casefold()
        ]
        physical_mice = _devices_with_physical_path(mouse_devices)
        if physical_mice:
            return physical_mice

        pointer_devices = [
            device
            for device in devices
            if any(
                marker in device[1].casefold()
                for marker in (
                    "touchpad",
                    "trackpad",
                    "trackpoint",
                    "pointing stick",
                )
            )
        ]
        physical_pointers = _devices_with_physical_path(pointer_devices)
        if physical_pointers:
            return physical_pointers
        return mouse_devices or pointer_devices

    return []


def _sort_physical_devices_first(
    devices: list[tuple[Path, str]],
) -> list[tuple[Path, str]]:
    return sorted(
        devices,
        key=lambda device: "[phys:" not in device[1].casefold(),
    )


def _devices_with_physical_path(
    devices: list[tuple[Path, str]],
) -> list[tuple[Path, str]]:
    return [device for device in devices if "[phys:" in device[1].casefold()]


def _describe_device(path: Path) -> str:
    event_name = path.name
    if path.parent == INPUT_DEVICES_PATH:
        event_name = path.resolve().name

    device_sysfs_path = SYSFS_INPUT_DEVICES_PATH / event_name / "device"
    try:
        device_name = (device_sysfs_path / "name").read_text(encoding="utf-8").strip()
    except OSError:
        device_name = ""

    if not device_name:
        return path.name if path.parent == INPUT_DEVICES_PATH else str(path)

    try:
        physical_path = (device_sysfs_path / "phys").read_text(encoding="utf-8").strip()
    except OSError:
        physical_path = ""

    label = f"{device_name} — {path}"
    if physical_path:
        label += f" [phys: {physical_path}]"
    return label


def abs_input_device_path(device: str) -> str:
    """Resolve by-id names and raw event paths to their device node."""
    device_path = Path(device)
    if device_path.is_absolute():
        return str(device_path)
    if RAW_EVENT_NAME_PATTERN.fullmatch(device):
        return str(RAW_INPUT_DEVICES_PATH / device_path)
    return str(INPUT_DEVICES_PATH / device_path)
