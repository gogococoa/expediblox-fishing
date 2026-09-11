import os
import sys
import time
import cv2
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
    cv2.destroyAllWindows()
    sys.exit(0)


keyboard.add_hotkey("f1", toggle_bot)
keyboard.add_hotkey("q", cleanup_and_exit)

print("[+] Inspection Mode Active.")
print("[+] Press [F1] to START/PAUSE bot.")
print("[+] Press [Q] to QUIT.\n")

with mss.MSS() as sct:
    action = "PAUSED"
    while True:
        idle_sct = sct.grab(IDLE_REGION)
        tracker_sct = sct.grab(TRACKER_REGION)

        state = state_detector.detect_state(idle_sct)
        is_inside, metrics, debug_frame = tracker.process_frame(tracker_sct)

        
        if state == "IDLE":
            action = "CAST"
        else:
            # Parse positions directly for inspection
            fish_x = 0
            bar_center = 0

            if "FishX:" in metrics and "Bar:[" in metrics:
                try:
                    fish_part = metrics.split("|")[0]
                    bar_part = metrics.split("|")[1]
                    fish_x = int(fish_part.split(":")[1].strip())
                    bar_bounds = bar_part.split("[")[1].split("]")[0].split("-")
                    bar_x_start = int(bar_bounds[0])
                    bar_x_end = int(bar_bounds[1])
                    bar_center = (bar_x_start + bar_x_end) // 2
                except Exception:
                    pass

            # Containment logic decision
            if fish_x > 0 and bar_center > 0:
                if fish_x > bar_center:
                    action = "RIGHT_PULSE"
                else:
                    action = "LEFT_WAIT"
            else:
                action = "LEFT_WAIT"

            # Real-time console inspection readout
            print(
                f"[INSPECT] State: {state} | FishX: {fish_x} | BarCenter: {bar_center} | Action: {action}",
                end="\r",
            )

        active_prefix = "[BOT: ACTIVE]" if bot_active else "[BOT: PAUSED]"
        ahk.send_state(action, f"{active_prefix} [{state}] {metrics}")

        time.sleep(0.01)