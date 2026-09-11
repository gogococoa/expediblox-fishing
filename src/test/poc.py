import os
import subprocess
import time

# Absolute path to AutoHotkey v2 executable
AHK_PATH = r"C:\Program Files\AutoHotkey\v2\AutoHotkey.exe"

# Resolve hand.ahk path relative to this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AHK_SCRIPT = os.path.join(BASE_DIR, "actions", "hand.ahk")

# Target coordinates
TARGET_X = 564
TARGET_Y = 1049


def test_ahk_input(x, y):
    print(f"Sending input command to AHK for X: {x}, Y: {y}...")

    # Execute AHK process with coordinates as command-line arguments
    process = subprocess.Popen([AHK_PATH, AHK_SCRIPT, str(x), str(y)])

    # Wait for AHK process to complete execution
    process.wait()
    print("AHK execution completed successfully!")


if __name__ == "__main__":
    print("Starting Proof of Concept test in 3 seconds...")
    print("Move your hands away from mouse/keyboard.")
    time.sleep(3)

    test_ahk_input(TARGET_X, TARGET_Y)