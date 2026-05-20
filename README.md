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

**Troubleshooting Manual Testing:**
If you run the script manually in the terminal and receive a `[Errno 16] Device or resource busy` error, it means you have a background Systemd service currently running! The script requires an exclusive lock on the hardware. Simply run `sudo systemctl stop keyboard_chattering` or `sudo systemctl stop mouse_chattering` to release the lock before testing manually.

*Note: Legacy raw nodes (like those ending simply in `-mouse` or `-kbd` without the word `event`) are legacy X11 nodes and cannot be read by `libevdev`.*

## Installation

Download the repository and extract the files. The dependencies are listed in `requirements.txt`. You can install them with the command below. 

*(Note: According to PEP 668, newer Linux distributions may require the `--break-system-packages` flag, or the use of a python `venv`)*.

```shell
sudo pip install -r requirements.txt --break-system-packages
```

### Python Virtual Environment
Using the built-in `venv` module is the safest and cleanest way to run this tool.
```shell
# 1. Create a virtual environment named 'venv' inside the project folder
python -m venv venv

# 2. Activate the virtual environment
source venv/bin/activate

# 3. Install the dependencies inside the isolated environment
pip install -r requirements.txt
```

## Usage

`cd` inside the location of the extracted folder. Because keyboards and mice are handled differently by the OS, they are executed as separate modules. Enter the commands below to run them manually:

**To run the Keyboard fix:**
```shell
sudo python -m src.keyboard_main
```

**To run the Mouse fix:**
```shell
sudo python -m src.mouse_main
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

## Automation (Systemd)

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

**Example keyboard_chattering.service:**
```shell
ExecStart=/home/foouser/Downloads/HardwareChatteringFix-Linux/keyboard_chattering.sh
```

**Example mouse_chattering.service:**
```shell
ExecStart=/home/foouser/Downloads/HardwareChatteringFix-Linux/mouse_chattering.sh
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

### Step 5: Applying Changes

If you modify the service files, reload the daemon and restart the services to apply the changes:

**For the Keyboard:**
```shell
sudo systemctl daemon-reload
sudo systemctl reenable keyboard_chattering.service
sudo systemctl restart keyboard_chattering.service
```

**For the Mouse:**
```shell
sudo systemctl daemon-reload
sudo systemctl reenable mouse_chattering.service
sudo systemctl restart mouse_chattering.service
```

## Automation (Non-Systemd & BSD)

Because the Python scripts rely natively on the OS Kernel (`evdev` and `uinput`), the code works perfectly on non-systemd distributions and BSD variants. Ensure your `.sh` scripts are configured and executable (`chmod +x`), then use the guide below for your specific init system.

**PRO-TIP FOR LOGGING:** Since non-systemd systems lack `journalctl`, you should modify your `.sh` scripts to redirect output so you can read the logs. Append this to the execution lines in your `.sh` files:
`... -t 30 >> /var/log/keyboard_fix.log 2>&1` (Do the same for `mouse_fix.log`).
You can then read your logs anytime using `cat /var/log/keyboard_fix.log`.

### Cron (Universal Fallback)
The easiest way to run the scripts on any system without Systemd is using `cron`'s `@reboot` directive.
1. Open the root crontab: `sudo crontab -e`
2. Add both scripts to run in the background (using `&`):
   ```text
   @reboot /absolute/path/to/keyboard_chattering.sh &
   @reboot /absolute/path/to/mouse_chattering.sh &
   ```
- **Start Right Now:** Run `sudo /absolute/path/to/keyboard_chattering.sh &` in your terminal.
- **Status/Logs:** Run `ps aux | grep python3` to ensure they are running. View the `.log` files defined in your script.
- **Restart:** Run `sudo pkill -f keyboard_main` (or `mouse_main`), then manually start them again.

### OpenRC (Artix, Alpine, Gentoo)
1. Create two files: `/etc/init.d/keyboard_fix` and `/etc/init.d/mouse_fix`
2. Paste this template (Adjust names/paths for the mouse version!):
   ```bash
   #!/sbin/openrc-run
   name="Keyboard Chattering Fix"
   command="/absolute/path/to/keyboard_chattering.sh"
   command_background=true
   pidfile="/run/keyboard_fix.pid"
   depend() { need localmount }
   ```
3. Make them executable: `sudo chmod +x /etc/init.d/keyboard_fix /etc/init.d/mouse_fix`
4. Enable at boot: `sudo rc-update add keyboard_fix default` and `sudo rc-update add mouse_fix default`
- **Start Right Now / Restart:** `sudo rc-service keyboard_fix start` (or `restart`)
- **Status:** `sudo rc-service keyboard_fix status`

### Runit (Void Linux)
1. Create service directories: `sudo mkdir -p /etc/sv/keyboard_fix /etc/sv/mouse_fix`
2. Create a run file for the keyboard: `sudo nano /etc/sv/keyboard_fix/run`
   ```bash
   #!/bin/sh
   exec /absolute/path/to/keyboard_chattering.sh
   ```
3. Create a run file for the mouse: `sudo nano /etc/sv/mouse_fix/run`
   ```bash
   #!/bin/sh
   exec /absolute/path/to/mouse_chattering.sh
   ```
4. Make both executable: `sudo chmod +x /etc/sv/keyboard_fix/run /etc/sv/mouse_fix/run`
5. Enable them: `sudo ln -s /etc/sv/keyboard_fix /var/service/` and `sudo ln -s /etc/sv/mouse_fix /var/service/`
- **Start Right Now:** Runit detects the symlinks and starts them automatically!
- **Status:** `sudo sv status keyboard_fix mouse_fix`
- **Restart:** `sudo sv restart keyboard_fix mouse_fix`

### SysVinit (Devuan, Older Distros)
Simply add the executable scripts to your `/etc/rc.local` file before the `exit 0` line:
```bash
/absolute/path/to/keyboard_chattering.sh &
/absolute/path/to/mouse_chattering.sh &
exit 0
```
- **Start Right Now:** Run `sudo /etc/rc.local`
- **Status / Restart:** Use `ps aux | grep python3` to check status, and `kill` them to stop them.

### FreeBSD / BSD Family
FreeBSD has native support for `evdev`, but you must load the modules and adjust device paths.

**1. Load evdev modules:** Add these to `/boot/loader.conf` and reboot (or `kldload` them now):
```text
evdev_load="YES"
uinput_load="YES"
```

**2. Find your Device Path:** 
FreeBSD does not use Linux's `udev` naming conventions. The folder `/dev/input/by-id/` does not exist on BSD! Instead, FreeBSD lists devices as raw event nodes (`/dev/input/event0`, `event1`, etc.).
Update your `.sh` scripts to pass the raw absolute path directly to `-k` or `-m` (which overrides the auto-search scripts):
```bash
# Example keyboard_chattering.sh
cd /path/to/folder && sudo python3 -m src.keyboard_main -k /dev/input/event0 -t 30 >> /var/log/keyboard_fix.log 2>&1
```

**3. Automate using `rc.d` scripts:**
Create two files at `/usr/local/etc/rc.d/keyboard_fix` and `/usr/local/etc/rc.d/mouse_fix`. Here is the keyboard template (duplicate and adjust variables for the mouse):
```bash
#!/bin/sh
# REQUIRE: DAEMON
# PROVIDE: keyboard_fix

. /etc/rc.subr

name="keyboard_fix"
rcvar="keyboard_fix_enable"
# Use daemon to securely background the python script
command="/usr/sbin/daemon"
command_args="-p /var/run/keyboard_fix.pid -f /absolute/path/to/keyboard_chattering.sh"

load_rc_config $name
run_rc_command "$1"
```
Make them executable (`sudo chmod +x /usr/local/etc/rc.d/*_fix`), then enable them in your `/etc/rc.conf`:
```text
keyboard_fix_enable="YES"
mouse_fix_enable="YES"
```
- **Start Right Now / Restart:** `sudo service keyboard_fix start` (or `restart`)
- **Status:** `sudo service keyboard_fix status`

*(Note: If your device disconnects, is unplugged, or goes to sleep, the Python script will gracefully exit. Systemd will then safely attempt to restart it every 5 seconds in the background until the device is reconnected, ensuring 0% CPU waste!)*
