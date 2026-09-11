import cv2
import numpy as np


class FishingDetector:
    def __init__(self, roi_left=500, roi_top=980, roi_width=920, roi_height=30):
        self.roi_left = roi_left
        self.roi_top = roi_top
        self.roi_width = roi_width
        self.roi_height = roi_height

        # HSV Thresholds
        self.lower_blue = np.array([85, 140, 120])
        self.upper_blue = np.array([115, 255, 255])

        self.lower_fish = np.array([0, 0, 180])
        self.upper_fish = np.array([180, 80, 255])

        # Wide horizontal kernel to bridge fish split on capture bar
        self.bridge_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 3))

    def process_frame(self, frame, draw_gizmos=False):
        """Processes a full screenshot frame and returns minigame state data."""
        h, w = frame.shape[:2]

        # Ensure frame dimensions accommodate ROI
        if h < self.roi_top + self.roi_height or w < self.roi_left + self.roi_width:
            return {"detected": False, "is_inside": False, "fish_x": None, "bar_bounds": None}

        roi = frame[
            self.roi_top : self.roi_top + self.roi_height,
            self.roi_left : self.roi_left + self.roi_width,
        ]
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        # 1. Detect Capture Bar
        mask_blue = cv2.inRange(hsv, self.lower_blue, self.upper_blue)
        mask_blue_closed = cv2.morphologyEx(
            mask_blue, cv2.MORPH_CLOSE, self.bridge_kernel
        )

        blue_contours, _ = cv2.findContours(
            mask_blue_closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        bar_x_start, bar_x_end = None, None
        bar_box = None

        if blue_contours:
            valid_bars = []
            for c in blue_contours:
                bx, by, bw, bh = cv2.boundingRect(c)
                aspect_ratio = bw / float(bh) if bh > 0 else 0
                if 40 <= bw <= 450 and 8 <= bh <= 25 and aspect_ratio >= 2.5:
                    valid_bars.append((c, bw * bh, bx, by, bw, bh))

            if valid_bars:
                _, _, bx, by, bw, bh = max(valid_bars, key=lambda x: x[1])
                bar_x_start = self.roi_left + bx
                bar_x_end = self.roi_left + bx + bw
                bar_box = (bx, by, bw, bh)

        # 2. Detect Fish
        mask_fish = cv2.inRange(hsv, self.lower_fish, self.upper_fish)
        fish_contours, _ = cv2.findContours(
            mask_fish, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        fish_x, fish_y = None, None
        fish_box = None

        if fish_contours:
            for c in sorted(fish_contours, key=cv2.contourArea, reverse=True):
                area = cv2.contourArea(c)
                if 15 < area < 800:
                    fx, fy, fw, fh = cv2.boundingRect(c)
                    aspect_ratio = fw / float(fh) if fh > 0 else 0
                    if 0.5 <= aspect_ratio <= 2.2:
                        fish_x = self.roi_left + fx + (fw // 2)
                        fish_y = self.roi_top + fy + (fh // 2)
                        fish_box = (fx, fy, fw, fh)
                        break

        # 3. Containment Logic
        is_inside = False
        detected = bar_x_start is not None and fish_x is not None
        if detected:
            is_inside = bar_x_start <= fish_x <= bar_x_end

        # Optional Gizmo Rendering
        if draw_gizmos:
            if bar_box:
                bx, by, bw, bh = bar_box
                cv2.rectangle(
                    frame,
                    (self.roi_left + bx, self.roi_top + by),
                    (self.roi_left + bx + bw, self.roi_top + by + bh),
                    (0, 255, 0),
                    2,
                )
            if fish_box:
                fx, fy, fw, fh = fish_box
                cv2.rectangle(
                    frame,
                    (self.roi_left + fx, self.roi_top + fy),
                    (self.roi_left + fx + fw, self.roi_top + fy + fh),
                    (0, 0, 255),
                    2,
                )
                cv2.circle(frame, (fish_x, fish_y), 3, (0, 0, 255), -1)

            status_text = f"STATUS: [{'INSIDE' if is_inside else 'OUTSIDE'}]"
            cv2.putText(
                frame,
                status_text,
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0) if is_inside else (0, 0, 255),
                2,
            )

        return {
            "detected": detected,
            "is_inside": is_inside,
            "fish_x": fish_x,
            "bar_bounds": (bar_x_start, bar_x_end) if detected else None,
        }