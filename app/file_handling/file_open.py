import os
import sys
import subprocess
# ---------------- open file ----------------
def open_file(path):
    if not path or not os.path.exists(path):
        return

    try:
        if sys.platform.startswith("win"):
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception as e:
        print("Open failed:", e)
