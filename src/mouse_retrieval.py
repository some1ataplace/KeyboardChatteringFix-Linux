from typing import Final

from src.input_retrieval import abs_input_device_path, retrieve_input_device_name

INPUT_DEVICES_PATH: Final = "/dev/input/by-id"


def retrieve_mouse_name() -> str:
    return retrieve_input_device_name("mouse")


def abs_mouse_path(device: str) -> str:
    return abs_input_device_path(device)
