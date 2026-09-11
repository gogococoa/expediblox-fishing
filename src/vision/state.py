import cv2
import numpy as np


class GameStateDetector:

    def __init__(
        self, idle_region={"left": 10, "top": 980, "width": 75, "height": 70}
    ):
        self.region = idle_region

        # Idle Button Cyan HSV Range (#24D2FF)
        self.lower_idle_cyan = np.array([85, 150, 180])
        self.upper_idle_cyan = np.array([105, 255, 255])

    def detect_state(self, sct_img):
        frame_rgba = np.ascontiguousarray(sct_img)
        frame = cv2.cvtColor(frame_rgba, cv2.COLOR_BGRA2BGR)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        mask_idle = cv2.inRange(hsv, self.lower_idle_cyan, self.upper_idle_cyan)
        cyan_pixel_count = cv2.countNonZero(mask_idle)

        is_idle = cyan_pixel_count > 150
        return "IDLE" if is_idle else "FISHING"