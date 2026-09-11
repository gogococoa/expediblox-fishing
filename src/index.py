import os
import sys
import time
import keyboard
import mss

from actions.hand import AHKController
from vision.state import GameStateDetector
from vision.tracker import MinigameTracker

TRACKER_REGION = {
    "left": 500,
    "top": 976,
    "width": 1420 - 500,
    "height": 1005 - 976,
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

bot_active = False


def toggle_bot():
    global bot_active
    bot_active = not bot_active
    status = "RUNNING" if bot_active else "PAUSED"
    print(f"\n[!] BOT TOGGLED -> {status}\n")


def cleanup_and_exit():
    try:
        keyboard.unhook_all()
    except Exception:
        pass
    ahk.close()
    sys.exit(0)


keyboard.add_hotkey("f1", toggle_bot)
keyboard.add_hotkey("q", cleanup_and_exit)

print("[+] High-Performance Engine Running.")
print("[+] Press [F1] to START/PAUSE bot.")
print("[+] Press [Q] to QUIT.\n")

with mss.mss() as sct:
    while True:
        if not bot_active:
            ahk.send_state("PAUSED", "BOT PAUSED")
            time.sleep(0.05)
            continue

        idle_sct = sct.grab(IDLE_REGION)
        state = state_detector.detect_state(idle_sct)

        if state == "IDLE":
            action = "CAST"
            metrics_str = "Casting..."
        else:
            tracker_sct = sct.grab(TRACKER_REGION)
            is_inside, fish_x, bar_center = tracker.process_frame(tracker_sct)

            if fish_x > 0 and bar_center > 0:
                action = "RIGHT_PULSE" if fish_x > bar_center else "LEFT_WAIT"
            else:
                action = "LEFT_WAIT"

            metrics_str = f"FishX:{fish_x} | BarCenter:{bar_center}"

        print(
            f"[RUNNING] State: {state} | Action: {action} | {metrics_str}      ",
            end="\r",
        )
        ahk.send_state(action, f"[{state}] {metrics_str}")