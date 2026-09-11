import cv2
import numpy as np


class MinigameTracker:

    def __init__(self, monitor_region):
        self.monitor = monitor_region

        # Capture Bar HSV Range
        self.lower_blue = np.array([85, 140, 120])
        self.upper_blue = np.array([115, 255, 255])

        # Fish Icon HSV Range
        self.lower_fish = np.array([0, 0, 180])
        self.upper_fish = np.array([180, 80, 255])

        # Wide horizontal kernel to bridge the gap when fish overlaps the bar
        self.bridge_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 3))

    def process_frame(self, sct_img):
        # Convert MSS screen capture to a contiguous BGR image array
        frame_rgba = np.ascontiguousarray(sct_img)
        frame = cv2.cvtColor(frame_rgba, cv2.COLOR_BGRA2BGR)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # --- 1. Detect Capture Bar (with Morphological Bridging) ---
        mask_blue = cv2.inRange(hsv, self.lower_blue, self.upper_blue)
        mask_blue_bridged = cv2.morphologyEx(
            mask_blue, cv2.MORPH_CLOSE, self.bridge_kernel
        )

        blue_contours, _ = cv2.findContours(
            mask_blue_bridged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        bar_x_start, bar_x_end = 0, 0
        if blue_contours:
            valid_bars = []
            for c in blue_contours:
                bx, by, bw, bh = cv2.boundingRect(c)
                aspect_ratio = bw / float(bh) if bh > 0 else 0

                # Filter out full track contours and noise
                if 40 <= bw <= 450 and 8 <= bh <= 25 and aspect_ratio >= 2.5:
                    valid_bars.append((c, bw * bh, bx, by, bw, bh))

            if valid_bars:
                # Select largest matching contour
                _, _, bx, by, bw, bh = max(valid_bars, key=lambda x: x[1])
                bar_x_start = bx
                bar_x_end = bx + bw

                # Draw Capture Bar box on memory frame
                cv2.rectangle(frame, (bx, by), (bx + bw, by + bh), (0, 255, 0), 2)

        # --- 2. Detect Fish Icon ---
        mask_fish = cv2.inRange(hsv, self.lower_fish, self.upper_fish)
        fish_contours, _ = cv2.findContours(
            mask_fish, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        fish_x = 0
        if fish_contours:
            for c in sorted(fish_contours, key=cv2.contourArea, reverse=True):
                area = cv2.contourArea(c)
                if 15 < area < 800:
                    fx, fy, fw, fh = cv2.boundingRect(c)
                    aspect_ratio = fw / float(fh) if fh > 0 else 0

                    if 0.5 <= aspect_ratio <= 2.2:
                        fish_x = fx + (fw // 2)
                        fish_y = fy + (fh // 2)

                        # Draw Fish box and center point on memory frame
                        cv2.rectangle(
                            frame, (fx, fy), (fx + fw, fy + fh), (0, 0, 255), 2
                        )
                        cv2.circle(frame, (fish_x, fish_y), 3, (0, 0, 255), -1)
                        break

        # --- 3. Evaluate Containment ---
        is_inside = False
        if bar_x_start > 0 and bar_x_end > 0 and fish_x > 0:
            is_inside = bar_x_start <= fish_x <= bar_x_end

        metrics = f"FishX:{fish_x} | Bar:[{bar_x_start}-{bar_x_end}]"
        return is_inside, metrics, frame