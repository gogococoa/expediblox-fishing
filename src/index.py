import os
import subprocess
import time
import cv2
import keyboard
import mss
import numpy as np

# Project paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AHK_SCRIPT = os.path.join(BASE_DIR, "actions", "hand.ahk")
AHK_EXE = r"C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe"

# Launch persistent AHK process with unbuffered Standard Input
print("[+] Launching persistent AHK process via Pipe...")
ahk_process = subprocess.Popen(
    [AHK_EXE, AHK_SCRIPT],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1,  # Line-buffered
)
time.sleep(0.5)


def send_click_to_ahk(x: int, y: int):
    """Sends coordinates directly to AHK standard input buffer (~0.1ms latency)."""
    try:
        ahk_process.stdin.write(f"{x},{y}\n")
        ahk_process.stdin.flush()
    except Exception as e:
        print(f"[-] Pipe communication error: {e}")


def cleanup_and_exit():
    """Clean exit handler for instant termination."""
    print("\n[-] Exiting program cleanly...")
    try:
        ahk_process.terminate()
    except Exception:
        pass
    cv2.destroyAllWindows()
    os._exit(0)


# Bind global instant termination hotkey
keyboard.add_hotkey("q", cleanup_and_exit)

# Monitor region for MSS
monitor = {
    "left": 500,
    "top": 976,
    "width": 1420 - 500,
    "height": 1005 - 976,
}

# --- Target Color Definition: #0071C2 Blue ---
lower_blue = np.array([92, 180, 140])
upper_blue = np.array([112, 255, 240])

with mss.mss() as sct:
    print(
        "[+] Brain active. Tracking #0071C2 target blue. Press 'q' ANYWHERE to exit."
    )

    while True:
        sct_img = sct.grab(monitor)
        frame = np.array(sct_img)[:, :, :3]
        debug_frame = frame.copy()

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Target mask using blue range
        mask = cv2.inRange(hsv, lower_blue, upper_blue)

        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            if cv2.contourArea(largest_contour) > 50:
                cv2.drawContours(
                    debug_frame, [largest_contour], -1, (0, 255, 0), 2
                )
                M = cv2.moments(largest_contour)
                if M["m00"] != 0:
                    local_x = int(M["m10"] / M["m00"])
                    local_y = int(M["m01"] / M["m00"])

                    global_x = monitor["left"] + local_x
                    global_y = monitor["top"] + local_y

                    print(
                        f"[Target Detected] Global X: {global_x}, Y: {global_y}"
                    )

                    # Send click through persistent pipe instantly
                    send_click_to_ahk(global_x, global_y)
                    time.sleep(0.3)  # Debounce click interval

        cv2.imshow("Minigame Detection Debug View", debug_frame)
        cv2.waitKey(1)
        time.sleep(0.01)