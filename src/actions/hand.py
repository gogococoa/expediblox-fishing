import os
import subprocess
import time


class AHKController:

    def __init__(
        self, ahk_exe=r"C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe"
    ):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.ahk_script = os.path.join(self.base_dir, "hand.ahk")
        self.ahk_exe = ahk_exe
        self.process = None
        self._start_process()

    def _start_process(self):
        print("[+] Launching persistent AHK process...")
        self.process = subprocess.Popen(
            [self.ahk_exe, self.ahk_script],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        time.sleep(0.5)

    def send_state(self, action: str, payload: str):
        if not self.process or self.process.poll() is not None:
            return

        try:
            # Clean stream output: "ACTION,PAYLOAD\n"
            self.process.stdin.write(f"{action},{payload}\n")
            self.process.stdin.flush()
        except Exception as e:
            print(f"[-] AHK Pipe Error: {e}")

    def close(self):
        if self.process:
            try:
                self.process.stdin.close()
                self.process.terminate()
            except Exception:
                pass
            print("[-] AHK Controller shut down.")