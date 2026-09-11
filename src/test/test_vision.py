import os
import cv2
import numpy as np

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "public", "gizmos")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Minigame track bounding box
ROI_LEFT = 500
ROI_TOP = 980
ROI_WIDTH = 920
ROI_HEIGHT = 30

TEST_IMAGES = [
    "fish-outside-fullscreen.png",
    "fish-inside-fullscreen.png",
]


def analyze_and_draw_gizmos(image_name):
    image_path = os.path.join(PROJECT_ROOT, image_name)
    if not os.path.exists(image_path):
        image_path = image_name

    if not os.path.exists(image_path):
        print(f"[-] File not found: {image_path}")
        return

    frame = cv2.imread(image_path)
    if frame is None:
        print(f"[-] Failed to load: {image_path}")
        return

    # Extract ROI
    roi = frame[
        ROI_TOP : ROI_TOP + ROI_HEIGHT, ROI_LEFT : ROI_LEFT + ROI_WIDTH
    ]
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    # --- 1. Capture Bar Detection ---
    lower_blue = np.array([85, 140, 120])
    upper_blue = np.array([115, 255, 255])
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)

    # Wide horizontal kernel (25x3) bridges the gap created by the overlapping fish
    bridge_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 3))
    mask_blue_bridged = cv2.morphologyEx(
        mask_blue, cv2.MORPH_CLOSE, bridge_kernel
    )

    blue_contours, _ = cv2.findContours(
        mask_blue_bridged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    bar_x_start, bar_x_end = None, None

    if blue_contours:
        valid_bars = []
        for c in blue_contours:
            bx, by, bw, bh = cv2.boundingRect(c)
            aspect_ratio = bw / float(bh) if bh > 0 else 0

            # Filter out minor noise and ensure reasonable capture bar bounds
            if 40 <= bw <= 450 and 8 <= bh <= 25 and aspect_ratio >= 2.5:
                valid_bars.append((c, bw * bh, bx, by, bw, bh))

        if valid_bars:
            # Select the largest combined capture bar
            _, _, bx, by, bw, bh = max(valid_bars, key=lambda x: x[1])
            bar_x_start = ROI_LEFT + bx
            bar_x_end = ROI_LEFT + bx + bw

            cv2.rectangle(
                frame,
                (ROI_LEFT + bx, ROI_TOP + by),
                (ROI_LEFT + bx + bw, ROI_TOP + by + bh),
                (0, 255, 0),
                2,
            )
            cv2.putText(
                frame,
                "CAPTURE BAR",
                (ROI_LEFT + bx, max(15, ROI_TOP + by - 5)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (0, 255, 0),
                1,
            )

    # --- 2. Fish Icon Detection ---
    lower_fish = np.array([0, 0, 180])
    upper_fish = np.array([180, 80, 255])
    mask_fish = cv2.inRange(hsv, lower_fish, upper_fish)

    fish_contours, _ = cv2.findContours(
        mask_fish, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    fish_x = None

    if fish_contours:
        for c in sorted(fish_contours, key=cv2.contourArea, reverse=True):
            area = cv2.contourArea(c)
            if 15 < area < 800:
                fx, fy, fw, fh = cv2.boundingRect(c)
                aspect_ratio = fw / float(fh) if fh > 0 else 0

                if 0.5 <= aspect_ratio <= 2.2:
                    fish_x = ROI_LEFT + fx + (fw // 2)
                    fish_y = ROI_TOP + fy + (fh // 2)

                    cv2.rectangle(
                        frame,
                        (ROI_LEFT + fx, ROI_TOP + fy),
                        (ROI_LEFT + fx + fw, ROI_TOP + fy + fh),
                        (0, 0, 255),
                        2,
                    )
                    cv2.circle(frame, (fish_x, fish_y), 3, (0, 0, 255), -1)
                    cv2.putText(
                        frame,
                        "FISH",
                        (ROI_LEFT + fx, max(15, ROI_TOP + fy - 5)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.4,
                        (0, 0, 255),
                        1,
                    )
                    break

    # --- 3. Containment Check ---
    is_inside = False
    if bar_x_start is not None and bar_x_end is not None and fish_x is not None:
        is_inside = bar_x_start <= fish_x <= bar_x_end

    status_text = (
        "STATUS: [ INSIDE ]" if is_inside else "STATUS: [ OUTSIDE ]"
    )
    status_color = (0, 255, 0) if is_inside else (0, 0, 255)

    cv2.putText(
        frame,
        status_text,
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        status_color,
        2,
    )

    output_path = os.path.join(
        OUTPUT_DIR, f"gizmo_{os.path.basename(image_name)}"
    )
    cv2.imwrite(output_path, frame)
    print(
        f"[+] {image_name} -> {status_text} | Bar: [{bar_x_start}, {bar_x_end}] | Fish X: {fish_x}"
    )

if __name__ == "__main__":
    for img in TEST_IMAGES:
        img_path = os.path.abspath(
            os.path.join(CURRENT_DIR, "..", "..", "public", img))
        analyze_and_draw_gizmos(img_path)