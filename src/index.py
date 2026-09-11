# Import module for handling file paths and operating system interactions
import os
# Import module to launch external programs (used here to run AutoHotkey)
import subprocess
import sys
# Import module for managing delays and execution timing
import time

# Import OpenCV for computer vision and image processing operations
import cv2

import keyboard
# Import MSS for ultra-fast, low-CPU screen capture on Windows
import mss
# Import NumPy for fast numerical and array manipulations on image frames
import numpy as np

# Define the precise screen area to capture (X: 500 to 1420, Y: 976 to 1005)
monitor = {
    "left": 500,  # X coordinate of the top-left corner
    "top": 976,  # Y coordinate of the top-left corner
    "width": 1420 - 500,  # Total width of the capture region (920 pixels)
    "height": 1005 - 976,  # Total height of the capture region (29 pixels)
}

# Absolute file path to the AutoHotkey v2 executable on your system
AHK_PATH = r"C:\Program Files\AutoHotkey\v2\AutoHotkey.exe"

# Get the directory where this current Python file resides
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Build the relative path to your hand.ahk script inside the actions folder
AHK_SCRIPT = os.path.join(BASE_DIR, "actions", "hand.ahk")


# Function to trigger AutoHotkey with target coordinates as arguments
def send_click_to_ahk(target_x, target_y):
    # Launch AHK as a non-blocking background process passing target X and Y
    subprocess.Popen([AHK_PATH, AHK_SCRIPT, str(target_x), str(target_y)])

def exit_app_instantly():
    print("\n[-] 'q' pressed! Killing program immediately...")
    # Properly destroy OpenCV windows before instant process exit
    cv2.destroyAllWindows()
    # Instantly terminates the main process from any thread
    os._exit(0)


# Bind global hotkey
keyboard.add_hotkey("q", exit_app_instantly)

# Initialize the MSS screen capture context manager
with mss.mss() as sct:
    # Print status message to console
    print("Brain initialized with MSS driver. (Press 'q' to exit)")

    # Start the continuous game-monitoring loop
    while True:
        # Capture raw pixel data from the specified screen region
        sct_img = sct.grab(monitor)

        # Convert raw capture data into a NumPy array and drop the alpha channel (keep BGR)
        frame = np.array(sct_img)[:, :, :3]

        # Make a fresh copy of the frame to draw visual debug graphics on
        debug_frame = frame.copy()

        # Convert image color space from BGR to HSV (easier to isolate specific colors)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Exact OpenCV HSV for #0071C2 is [102, 255, 194]

        # Lower bound (subtract tolerance for slight lighting variations)
        lower_blue = np.array([92, 180, 140])

        # Upper bound (add tolerance)
        upper_blue = np.array([112, 255, 240])

        # Create a binary black/white mask where red pixels are white and others are black
        mask = cv2.inRange(hsv, lower_blue, upper_blue)

        # Detect shapes/outer boundaries of all white pixel blobs in the mask
        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        # Check if any matching color contours were found
        if contours:
            # Pick the single largest contour matching the target color
            largest_contour = max(contours, key=cv2.contourArea)

            # Ensure the target is larger than 50 pixels to ignore random visual noise
            if cv2.contourArea(largest_contour) > 50:
                # Draw a green outline around the detected target on the debug frame
                cv2.drawContours(
                    debug_frame, [largest_contour], -1, (0, 255, 0), 2
                )

                # Calculate spatial moments to find the geometric center of the shape
                M = cv2.moments(largest_contour)

                # Prevent division by zero error if area moment is somehow zero
                if M["m00"] != 0:
                    # Calculate local X coordinate relative to cropped window top-left (0,0)
                    local_x = int(M["m10"] / M["m00"])

                    # Calculate local Y coordinate relative to cropped window top-left (0,0)
                    local_y = int(M["m01"] / M["m00"])

                    # Draw a solid red dot at the calculated center point on the debug view
                    cv2.circle(
                        debug_frame, (local_x, local_y), 4, (0, 0, 255), -1
                    )

                    # Convert local X to global desktop screen coordinate
                    global_x = monitor["left"] + local_x

                    # Convert local Y to global desktop screen coordinate
                    global_y = monitor["top"] + local_y

                    # Output the detected screen coordinates to the console
                    print(
                        f"[Target Detected] Global X: {global_x}, Y: {global_y}"
                    )

                    # Call function to send click action to AutoHotkey
                    send_click_to_ahk(global_x, global_y)

                    # Cooldown pause to prevent rapid re-clicking
                    time.sleep(0.5)

        # Render the debug frame in a pop-up window
        cv2.imshow("Minigame Detection Debug View", debug_frame)

        # Check if the user pressed the 'q' key while focusing the debug window
        if cv2.waitKey(1) & 0xFF == ord("q"):
            # Exit loop if 'q' was pressed
            break

        # Brief 10ms sleep to prevent maxing out CPU core utilization
        time.sleep(0.01)

# Safely close all created OpenCV preview windows on exit
cv2.destroyAllWindows()