import os
import sys
import time
import cv2
import keyboard
import mss

from actions.hand import AHKController
from vision.state import GameStateDetector
from vision.tracker import MinigameTracker

# Original focused regions
TRACKER_REGION = {
    "left": 500,
    "top": 980,
    "width": 1420 - 500,
    "height": 1010 - 980,
}

IDLE_REGION = {
    "left": 10,
    "top": 980,
    "width": 75,
    "height": 70,
}

ahk = AHKController()
tracker = MinigameTracker(TRACKER_REGION)
state_detector = GameStateDetector(IDLE_REGION)

# Bot Execution Flag
bot_active = False


def toggle_bot():
    global bot_active
    bot_active = not bot_active
    status = "RUNNING" if bot_active else "PAUSED"
    print(f"[!] Bot State Toggled: {status}")


def cleanup_and_exit():
    try:
        keyboard.unhook_all()
    except Exception:
        pass
    ahk.close()
    cv2.destroyAllWindows()
    sys.exit(0)
    os._exit(0)


# Hotkey registration
keyboard.add_hotkey("f1", toggle_bot)
keyboard.add_hotkey("q", cleanup_and_exit)

print("[+] Script Initialized.")
print("[+] Press [F1] to START / PAUSE the bot.")
print("[+] Press [Q] to QUIT completely.")

with mss.MSS() as sct:
    while True:
        # Capture dedicated regions
        idle_sct = sct.grab(IDLE_REGION)
        tracker_sct = sct.grab(TRACKER_REGION)

        state = state_detector.detect_state(idle_sct)
        is_inside, metrics, debug_frame = tracker.process_frame(tracker_sct)

        # Action evaluation based on bot state
        if bot_active:
            if state == "IDLE":
                action = "CAST"
            else:
                # Basic containment control logic: HOLD if outside, RELEASE if inside
                action = "RELEASE" if is_inside else "HOLD"
        else:
            action = "PAUSED"

        active_prefix = "[BOT: ACTIVE]" if bot_active else "[BOT: PAUSED]"
        
        # Send action directly as parameter 1 to AHK
        ahk.send_state(action, f"{active_prefix} [{state}] {metrics}")

        cv2.imshow("Tracker View", debug_frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            cleanup_and_exit()

        time.sleep(0.01)