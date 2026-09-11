import cv2
import numpy as np


class GameStateDetector:

    def __init__(
        self, idle_region={"left": 10, "top": 980, "width": 75, "height": 70}
    ):
        self.region = idle_region
        self.lower_idle_cyan = np.array([85, 150, 180])
        self.upper_idle_cyan = np.array([105, 255, 255])

    def detect_state(self, sct_img):
        # Drop alpha channel and convert BGR -> HSV
        frame_bgr = np.ascontiguousarray(sct_img)[:, :, :3]
        hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)

        mask_idle = cv2.inRange(hsv, self.lower_idle_cyan, self.upper_idle_cyan)
        cyan_pixel_count = cv2.countNonZero(mask_idle)

        return "IDLE" if cyan_pixel_count > 150 else "FISHING"