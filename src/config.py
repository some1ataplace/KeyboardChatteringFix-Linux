"""
Constants for keyboard chattering filter configuration.

PRECEDENCE RULES:
1. Command Line (--keys): Highest priority. If provided, this file is ignored.
2. This File (FILTERED_KEYS): Used if no command line argument is provided.
3. Empty: If BOTH the command line and this list are empty, ALL keys will be filtered.
"""

# To filter specific keys, add them to this set. 
# Example: FILTERED_KEYS = {"KEY_A", "KEY_SPACE", "KEY_ENTER"}
# Leave it empty as set() to filter ALL keys by default.
FILTERED_KEYS = set()


# ==========================================
# REFERENCE: COMMON KEY VALUES TO COPY/PASTE
# ==========================================
# Letters: 
# KEY_A, KEY_B, KEY_C, KEY_D, KEY_E, KEY_F, KEY_G, KEY_H, KEY_I, KEY_J, 
# KEY_K, KEY_L, KEY_M, KEY_N, KEY_O, KEY_P, KEY_Q, KEY_R, KEY_S, KEY_T, 
# KEY_U, KEY_V, KEY_W, KEY_X, KEY_Y, KEY_Z
#
# Numbers (Top Row): 
# KEY_1, KEY_2, KEY_3, KEY_4, KEY_5, KEY_6, KEY_7, KEY_8, KEY_9, KEY_0, KEY_MINUS, KEY_EQUAL
#
# Numpad: 
# KEY_KP0 to KEY_KP9, KEY_KPMINUS, KEY_KPPLUS, KEY_KPASTERISK, KEY_KPDOT, KEY_KPENTER
#
# Special/Control: 
# KEY_SPACE, KEY_ENTER, KEY_BACKSPACE, KEY_TAB, KEY_ESC, KEY_CAPSLOCK
# 
# Modifiers: 
# KEY_LEFTSHIFT, KEY_RIGHTSHIFT, KEY_LEFTCTRL, KEY_RIGHTCTRL, KEY_LEFTALT, KEY_RIGHTALT, KEY_LEFTMETA (Super/Windows)
# 
# Arrows & Navigation: 
# KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_HOME, KEY_END, KEY_PAGEUP, KEY_PAGEDOWN, KEY_INSERT, KEY_DELETE
# 
# Function Keys: 
# KEY_F1, KEY_F2, KEY_F3, KEY_F4, KEY_F5, KEY_F6, KEY_F7, KEY_F8, KEY_F9, KEY_F10, KEY_F11, KEY_F12
#
# Punctuation: 
# KEY_LEFTBRACE, KEY_RIGHTBRACE, KEY_SEMICOLON, KEY_APOSTROPHE, KEY_GRAVE, KEY_BACKSLASH, KEY_COMMA, KEY_DOT, KEY_SLASH
