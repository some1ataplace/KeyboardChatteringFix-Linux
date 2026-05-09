# __Keyboard Chattering & Mouse Double-Click Fix for Linux__

[![GitHub](https://img.shields.io/github/license/w2sv/KeyboardChatteringFix-Linux?)](LICENSE)

__A tool for filtering mechanical keyboard chattering and mouse double-clicking on Linux__

## The problem

Switches on mechanical keyboards occasionally start to "chatter" or "bounce", meaning when you press a key with a faulty switch it erroneously detects two or even more key presses. Similarly, mechanical switches on mice (especially gaming mice) frequently develop "double-click" issues where a single physical click registers as multiple rapid clicks.

## The existing solutions

Apart from buying new hardware, there have been ways to deal with this problem using software methods. The idea is to filter inputs that occur faster than a certain threshold. "Keyboard Chattering Fix v 0.0.1" is a tool I had been using on Windows for a long time, and these days you also have [Keyboard Chatter Blocker](https://github.com/mcmonkeyprojects/KeyboardChatterBlocker). 

Unfortunately, all existing tools only work on Windows. On Linux, the answer everyone seems to give is to use the Bounce Keys feature of X, but it's not really useful in this way. For one, it resets the delay even on filtered key presses, meaning that if you press the key fast enough, *none* of the presses will pass through, ever. 

## This project's solution

This tool attempts to solve these hardware problems by having full low-level access and control over all input events. Using `libevdev`'s Python bindings, it grabs your device and processes its events, then outputs the result back to the system using `/dev/uinput`. This effectively emulates a flawless keyboard and mouse that doesn't chatter or double-click, unlike your real ones!

This also means it works across the whole system, without depending on X11 or Wayland.

*Note for Mice:* To ensure your mouse cursor remains flawlessly smooth, this tool uses completely separate logic for mice. It natively bypasses X/Y cursor movement and scrolling, applying the chatter filter *only* to physical button clicks (Left click, Right click, Side buttons, etc.).

As for the filtering rule, what seems to work well is the time between the last "key up" event and the current "key down" event. When the switch chatters, that time is very low - around 10 ms. By filtering such anomalies, we remove chatter without impeding actual fast typing or clicking.

### Understanding Linux Input Devices (Which one do I pick?)

Modern gaming peripherals (like Corsair, Razer, or Logitech) are "composite USB devices". This means a single physical mouse might tell Linux it is actually 4 different devices! When you run the scripts manually, you will see a list of endpoints ending in different suffixes. 

Here is a guide on which one to choose:

- **`-event-kbd`**: The primary endpoint for standard keystrokes. For keyboards, select this to fix chattering on standard keys (A-Z, 0-9). 
- **`-event-mouse`**: The primary endpoint for standard mouse clicks (Left, Right, Middle) and X/Y movement. Select this to fix standard mouse double-clicking.
- **`-ifXX-event-kbd` (Virtual Mouse Keyboards)**: Advanced gaming mice often register a "virtual keyboard" to handle macro side-buttons. If your mouse's side buttons are double-clicking, you may need to point the mouse script at this endpoint instead of the standard mouse endpoint!
- **`-event-ifXX` (Interfaces)**: These handle multimedia controls (Volume wheels, Play/Pause) or vendor-specific data (RGB lighting). You rarely need to select these unless your volume wheel is bouncing.

*Note: Legacy raw nodes (like those ending simply in `-mouse` or `-kbd` without the word `event`) are legacy X11 nodes and cannot be read by `libevdev`.*

## Installation

Download the repository and extract the files. The dependencies are listed in `requirements.txt`. You can install them with the command below. 

*(Note: According to PEP 668, newer Linux distributions may require the `--break-system-packages` flag, or the use of a python `venv`)*.

```shell
sudo pip3 install -r requirements.txt --break-system-packages
```

## Usage

`cd` inside the location of the extracted folder. Because keyboards and mice are handled differently by the OS, they are executed as separate modules. Enter the commands below to run them manually:

**To run the Keyboard fix:**
```shell
sudo python3 -m src.keyboard_main
```

**To run the Mouse fix:**
```shell
sudo python3 -m src.mouse_main
```

### Customization Options

- `-k KEYBOARD`, `--keyboard KEYBOARD`
  - Name of your chattering keyboard device as listed in `/dev/input/by-id`. If left unset, it will attempt to retrieve it automatically. 
- `-m MOUSE`, `--mouse MOUSE`
  - Name of your double-clicking mouse device. Works identically to the keyboard argument above.
- `-t THRESHOLD`, `--threshold THRESHOLD`
  - Filter time threshold in milliseconds. Default=30ms. Note: This denotes the time between a key/button being *released* and pressed again. For reference, if you click really fast, this delay is around 50 ms.
- `--keys KEYS` (For Keyboard)
  - Comma-separated list of specific keys to filter (e.g., `KEY_A,KEY_SPACE`). If provided, *only* these keys will be filtered, leaving the rest of your keyboard untouched. You can also permanently define these in `src/keyboard_config.py`.
- `--buttons BUTTONS` (For Mouse)
  - Comma-separated list of specific buttons to filter (e.g., `BTN_LEFT,BTN_RIGHT`). You can also permanently define these in `src/mouse_config.py`.
- `-v {0,1,2}`, `--verbosity {0,1,2}`

## Automation

Starting the scripts manually every time is not ideal. You should set them up as background Systemd services. Because the keyboard and mouse scripts are separate, they can run concurrently in the background without interfering with one another.

### Step 1: Configure the shell scripts
Modify `keyboard_chattering.sh` and/or `mouse_chattering.sh` to `cd` into the absolute path of your downloaded folder, and input your device IDs and desired thresholds. 

**Example `keyboard_chattering.sh`:**
```shell
cd /home/foouser/Downloads/HardwareChatteringFix-Linux/ && sudo python3 -m src.keyboard_main -k usb-SINO_WEALTH_USB_KEYBOARD-event-kbd -t 40 --keys KEY_E,KEY_SPACE
```

**Example `mouse_chattering.sh`:**
```shell
cd /home/foouser/Downloads/HardwareChatteringFix-Linux/ && sudo python3 -m src.mouse_main -m usb-Logitech_Gaming_Mouse-event-mouse -t 50 --buttons BTN_LEFT,BTN_RIGHT
```

Make sure to change the file permissions so they are executable:
```shell
chmod +x keyboard_chattering.sh mouse_chattering.sh
```

### Step 2: Configure the service files
Edit `keyboard_chattering.service` and `mouse_chattering.service`. The `ExecStart` should be the absolute path of the respective `.sh` file. 

**Example:**
```shell
ExecStart=/home/foouser/Downloads/HardwareChatteringFix-Linux/keyboard_chattering.sh
```

### Step 3: Enable the Services (Separately or Combined)

Copy the `.service` files to your systemd folder:
```shell
sudo cp keyboard_chattering.service /etc/systemd/system/
sudo cp mouse_chattering.service /etc/systemd/system/
```

**To enable ONLY the keyboard fix:**
```shell
sudo systemctl enable --now keyboard_chattering
```

**To enable ONLY the mouse fix:**
```shell
sudo systemctl enable --now mouse_chattering
```

**To run BOTH concurrently:**
Simply run both enable commands! They operate completely independently of one another.
```shell
sudo systemctl enable --now keyboard_chattering
sudo systemctl enable --now mouse_chattering
```

### Step 4: Checking Status and Logs

You can check if the scripts are running properly by checking their independent statuses:

**For the Keyboard:**
```shell
systemctl status keyboard_chattering.service
journalctl -xeu keyboard_chattering.service
```

**For the Mouse:**
```shell
systemctl status mouse_chattering.service
journalctl -xeu mouse_chattering.service
```

*(Note: If your device disconnects, is unplugged, or goes to sleep, the service will safely pause and wait for it to reconnect without crashing or consuming CPU).*
