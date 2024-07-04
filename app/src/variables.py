import mss
import os

ROOT = None
HWND = None
BREAK = False
PATH = os.path.dirname(__file__).replace("src", "")

OS = os.name
with open(PATH.replace("\\app", "") + "version.txt") as f: VERSION = f.read()

RUN = True
WINDOWNAME = "PyTorch-Calculator"

FILE_PATH = None
FILE_CONTENT = []

CANVAS_POSITION = 0, 0
CANVAS_ZOOM = 1
CANVAS_TEMP = []
CANVAS_DRAW_COLOR = (255, 255, 255)

sct = mss.mss()
SCRENN_X = sct.monitors[1]["left"]
SCRENN_Y = sct.monitors[1]["top"]
SCREEN_WIDTH = sct.monitors[1]["width"]
SCREEN_HEIGHT = sct.monitors[1]["height"]

HWND = None
TK_HWND = None
CONSOLENAME = None
CONSOLEHWND = None

RED = "\033[91m"
GREEN = "\033[92m"
ORANGE = "\033[93m"
NORMAL = "\033[0m"