"""
Constants for mouse chattering filter configuration.

PRECEDENCE RULES:
1. Command Line (--buttons): Highest priority. If provided, this file is ignored.
2. This File (FILTERED_BUTTONS): Used if no command line argument is provided.
3. Empty: If BOTH the command line and this list are empty, ALL buttons will be filtered.
"""

# To filter specific buttons, add them to this set. 
# Example: FILTERED_BUTTONS = {"BTN_LEFT", "BTN_SIDE"}
# Leave it empty as set() to filter ALL mouse buttons by default.
FILTERED_BUTTONS = set()


# ==========================================
# REFERENCE: COMMON MOUSE BUTTON VALUES
# ==========================================
# Standard Clicks:
# BTN_LEFT    (Standard Left Click)
# BTN_RIGHT   (Standard Right Click)
# BTN_MIDDLE  (Scroll Wheel Click)
#
# Side / Gaming Buttons (Thumb buttons):
# BTN_SIDE    (Often defaults to "Back" in browsers)
# BTN_EXTRA   (Often defaults to "Forward" in browsers)
# BTN_FORWARD (Alternative Forward)
# BTN_BACK    (Alternative Back)
# BTN_TASK    (Sometimes used for DPI shifts or task views)
#
# Numbered Extra Buttons (For MMO mice like Razer Naga / Corsair Scimitar):
# BTN_0, BTN_1, BTN_2, BTN_3, BTN_4, BTN_5, BTN_6, BTN_7, BTN_8, BTN_9
#
# Note: Scroll wheel *scrolling* (up/down) is treated as movement (EV_REL), 
# not a button press, so it is natively bypassed by our script to prevent lag!
