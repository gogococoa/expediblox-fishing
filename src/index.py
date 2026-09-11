import sys
import os
import time
import cv2
import keyboard
import mss

from actions.hand import AHKController
from vision.tracker import MinigameTracker

MONITOR_REGION = {
    "left": 500,
    "top": 980,
    "width": 1420 - 500,
    "height": 1010 - 980,
}

ahk = AHKController()
tracker = MinigameTracker(MONITOR_REGION)


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
        sct_img = sct.grab(MONITOR_REGION)
        is_inside, metrics, debug_frame = tracker.process_frame(sct_img)

        # Stream containment flag + position metrics to AHK ToolTip
        ahk.send_state(is_inside, metrics)

        cv2.imshow("Debug View", debug_frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            cleanup_and_exit()

        time.sleep(0.01)