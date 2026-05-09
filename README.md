# __Keyboard & Mouse Chattering Fix for Linux__

[![GitHub](https://img.shields.io/github/license/w2sv/KeyboardChatteringFix-Linux?)](LICENSE)

__A tool for filtering mechanical keyboard and mouse chattering on Linux__

## The problem

Switches on mechanical keyboards occasionally start to "chatter",
meaning when you press a key with a faulty switch it erroneously detects
two or even more key presses. Similarly, mechanical switches on mice (especially gaming mice) frequently develop "double-click" issues where a single click registers as multiple clicks.

## The existing solutions

Apart from buying a new keyboard or mouse, there have been ways to deal
with this problem using software methods. The idea is to filter key presses
that occur faster than a certain threshold. "Keyboard Chattering Fix v 0.0.1"
is a tool I had been using on Windows for a long time, and these days you also have
[Keyboard Chatter Blocker](https://github.com/mcmonkeyprojects/KeyboardChatterBlocker),
which is a nice open source tool with some additional functionality. It's actually what
I use myself when I use Windows.

Unfortunately, all existing tools only work on Windows.
On Linux, the answer everyone seems to give is to use the Bounce Keys feature of X,
but it's not really useful in this way. For one, it resets the delay even on filtered
key presses, meaning that if you press the key fast enough,
*none* of the presses with pass through, ever. And if the key chatters,
this is bound to happen eventually and interfere with fast repeated key presses.

## This project's solution

This tool attempts to solve any such problems that may arise by having full low-level access
and control over all input events.
Using `libevdev`'s Python bindings, it grabs your keyboard's (or mouse's) event device and processes its events,
then outputs the result back to the system using `/dev/uinput`, effectively emulating a keyboard or mouse -
one that doesn't chatter, unlike your real one!

This also means it works across the system, without depending on X.

*Note for Mice:* To ensure your mouse cursor remains flawlessly smooth, this tool uses separate logic for mice. It natively bypasses X/Y cursor movement and scrolling, applying the chatter filter *only* to physical button clicks.

As for the filtering rule, what seems to work well is the time between the last key up event
and the current key down event. When the key chatters, that time seems to be very low - around 10 ms.
By filtering such anomalies, we can hopefully remove chatter without impeding actual fast key presses.

## Installation

Download the repository as a zip and extract the file. The dependencies are listed in the requirements.txt. And you can install it with the command below. 

*(Note: According to PEP 668, newer Linux distributions may require the `--break-system-packages` flag, or the use of a python `venv`)*.

```shell
sudo pip3 install -r requirements.txt --break-system-packages
```

## Usage

`cd` inside the location of the extracted folder. Because keyboards and mice are handled differently by the OS, they are executed as separate modules. Enter the commands below to run them.

**For Keyboard:**
```shell
sudo python3 -m src.keyboard_main
```

**For Mouse:**
```shell
sudo python3 -m src.mouse_main
```

### Customization Options

- -k KEYBOARD, --keyboard KEYBOARD
  - Name of your chattering keyboard device as listed in /dev/input/by-id. If left unset, will be attempted to be retrieved
  automatically. The device is captured `by-id`, and therefore in a persistent way.

- -m MOUSE, --mouse MOUSE
  - Name of your chattering mouse device. Works identically to the keyboard argument above.

- -t THRESHOLD, --threshold THRESHOLD
  - Filter time threshold in milliseconds. Default=30ms. Note: This does not denote the time between key presses, but
    between a key being released and pressed again, so the number should probably be lower than you might think. For reference, if you press the key really fast this delay is around 50 ms.

- --keys KEYS (For Keyboard)
  - Comma-separated list of specific keys to filter (e.g., `KEY_A,KEY_SPACE`). If provided, *only* these keys will be filtered, leaving the rest of your keyboard untouched. You can also permanently define these in `src/keyboard_config.py`.

- --buttons BUTTONS (For Mouse)
  - Comma-separated list of specific buttons to filter (e.g., `BTN_LEFT,BTN_RIGHT`). You can also permanently define these in `src/mouse_config.py`.

- -v {0,1,2}, --verbosity {0,1,2}

## Automation

Starting the script manually every time doesn't sound like the greatest idea, so
you should probably consider something that does it for you. Modify `keyboard_chattering.sh` and/or `mouse_chattering.sh` to `cd` into the absolute path of the downloaded folder and input the device id and the desired threshold. For example:
```shell
cd /home/foouser/Downloads/KeyboardChatteringFix-Linux-master/ && sudo python3 -m src.keyboard_main -k usb-SINO_WEALTH_USB_KEYBOARD-event-kbd -t 50
```
Also, make sure to change the file permission of the `.sh` scripts so that they are executable.
```shell
chmod +x keyboard_chattering.sh mouse_chattering.sh
```
The `.service` files should also be edited. The `ExecStart` should be the absolute path of the respective `.sh` file. For example:
```shell
ExecStart=/home/foouser/Downloads/KeyboardChatteringFix-Linux-master/keyboard_chattering.sh
```
Then, copy the `.service` files to `/etc/systemd/system/` and enable them with the commands below.
```shell
sudo systemctl enable --now keyboard_chattering
sudo systemctl enable --now mouse_chattering
```
You can check if the systemd unit files are properly working using 
```shell
systemctl status keyboard_chattering.service
```
You can also use 
```shell
journalctl -xeu keyboard_chattering.service
```
just to make sure that there are no errors. *(Note: If your device disconnects or goes to sleep, the service will safely pause and wait for it to reconnect without consuming CPU).*
