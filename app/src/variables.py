import src.settings as settings
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

FPS = 60
THEME = settings.Get("UI", "theme", "dark")

FILE_PATH = None
CANVAS_CONTENT = []

CANVAS_POSITION = (settings.Get("UI", "width", 1000) - 10) // 2, (settings.Get("UI", "height", 600) - 50) // 2
CANVAS_ZOOM = 1
CANVAS_SHOW_GRID = True
CANVAS_GRID_TYPE = "DOT"
CANVAS_TEMP = []
CANVAS_DELETE_LIST = []
CANVAS_DRAW_COLOR = (255, 255, 255)

TOOLBAR = None
TOOLBAR_HOVERED = False
TOOLBAR_WIDTH = None
TOOLBAR_HEIGHT = None
TOOLBAR_ROWS = None
TOOLBAR_COLUMNS = 3
TOOLBAR_PADDING = 10

DEFAULT_MOUSE_SPEED = 10

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