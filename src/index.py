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


def cleanup_and_exit():
    try:
        keyboard.unhook_all()
    except Exception:
        pass
    ahk.close()
    cv2.destroyAllWindows()
    sys.exit(0)
    os._exit(0)


keyboard.add_hotkey("q", cleanup_and_exit)

print("[+] Manual Test Active. Play manually and observe the HUD ToolTip.")

with mss.MSS() as sct:
    while True:
        # Capture dedicated regions
        idle_sct = sct.grab(IDLE_REGION)
        tracker_sct = sct.grab(TRACKER_REGION)

        state = state_detector.detect_state(idle_sct)
        is_inside, metrics, debug_frame = tracker.process_frame(tracker_sct)

        # Stream state + metrics to AHK pipe
        ahk.send_state(is_inside, f"[{state}] {metrics}")

        cv2.imshow("Tracker View", debug_frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            cleanup_and_exit()

        time.sleep(0.01)