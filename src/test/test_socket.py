import os
import subprocess
import time

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
AHK_SCRIPT = os.path.abspath(
    os.path.join(CURRENT_DIR, "..", "actions", "hand.ahk")
)
AHK_EXE = r"C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe"

print(f"[1] Launching AHK script from: {AHK_SCRIPT}")

process = subprocess.Popen(
    [AHK_EXE, AHK_SCRIPT],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1,
)

time.sleep(1)

print("[2] Sending click commands over Pipe...")
process.stdin.write("500,500\n")
process.stdin.flush()

time.sleep(1.5)

process.stdin.write("800,400\n")
process.stdin.flush()

time.sleep(1.5)

process.terminate()
print("[+] Test completed.")