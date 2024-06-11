import mss
import os

PATH = os.path.dirname(__file__).replace("src", "")

OS = os.name
with open(PATH.replace("\\app", "") + "version.txt") as f: VERSION = f.read()

RUN = True
WINDOWNAME = "PyTorch-Calculator"

sct = mss.mss()
SCRENN_X = sct.monitors[1]["left"]
SCRENN_Y = sct.monitors[1]["top"]
SCREEN_WIDTH = sct.monitors[1]["width"]
SCREEN_HEIGHT = sct.monitors[1]["height"]

CONSOLENAME = None
CONSOLEHWND = None

RED = "\033[91m"
GREEN = "\033[92m"
ORANGE = "\033[93m"
NORMAL = "\033[0m"