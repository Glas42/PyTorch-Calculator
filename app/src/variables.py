import src.settings as settings
import os

OS = os.name
PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__))).replace("\\", "/") + "/"
with open(PATH + "config/version.txt") as f: VERSION = f.read()
REMOTE_VERSION = None
CHANGELOG = None

LANGUAGE = settings.Get("UI", "Language", "en")
THEME = settings.Get("UI", "Theme", "Dark")
BACKGROUND = None
DEVMODE = False
CANVAS = None

X = None
Y = None
WIDTH = None
HEIGHT = None

HWND = None
NAME = "PyTorch-Calculator"
PAGE = settings.Get("UI", "PAGE", "Canvas")
BREAK = False
FPS = 60

CONSOLENAME = None
CONSOLEHWND = None

FONT_SIZE = 11
POPUP_HEIGHT = 50
TITLE_BAR_HEIGHT = 50
TEXT_COLOR = (255, 255, 255) if THEME == "Dark" else (0, 0, 0)
GRAYED_TEXT_COLOR = (155, 155, 155) if THEME == "Dark" else (100, 100, 100)
BACKGROUND_COLOR = (28, 28, 28) if THEME == "Dark" else (250, 250, 250)
TAB_BAR_COLOR = (47, 47, 47) if THEME == "Dark" else (231, 231, 231)
TAB_BUTTON_COLOR = (47, 47, 47) if THEME == "Dark" else (231, 231, 231)
TAB_BUTTON_HOVER_COLOR = (41, 41, 41) if THEME == "Dark" else (244, 244, 244)
TAB_BUTTON_SELECTED_COLOR = (28, 28, 28) if THEME == "Dark" else (250, 250, 250)
TAB_BUTTON_SELECTED_HOVER_COLOR = (28, 28, 28) if THEME == "Dark" else (250, 250, 250)
POPUP_COLOR = (42, 42, 42) if THEME == "Dark" else (236, 236, 236)
POPUP_HOVER_COLOR = (42, 42, 42) if THEME == "Dark" else (236, 236, 236)
POPUP_PROGRESS_COLOR = (255, 200, 87) if THEME == "Dark" else (184, 95, 0)
BUTTON_COLOR = (42, 42, 42) if THEME == "Dark" else (236, 236, 236)
BUTTON_HOVER_COLOR = (47, 47, 47) if THEME == "Dark" else (231, 231, 231)
BUTTON_SELECTED_COLOR = (28, 28, 28) if THEME == "Dark" else (250, 250, 250)
BUTTON_SELECTED_HOVER_COLOR = (28, 28, 28) if THEME == "Dark" else (250, 250, 250)
SWITCH_COLOR = (70, 70, 70) if THEME == "Dark" else (208, 208, 208)
SWITCH_KNOB_COLOR = (28, 28, 28) if THEME == "Dark" else (250, 250, 250)
SWITCH_HOVER_COLOR = (70, 70, 70) if THEME == "Dark" else (208, 208, 208)
SWITCH_ENABLED_COLOR = (255, 200, 87) if THEME == "Dark" else (184, 95, 0)
SWITCH_ENABLED_HOVER_COLOR = (255, 200, 87) if THEME == "Dark" else (184, 95, 0)
DROPDOWN_COLOR = (42, 42, 42) if THEME == "Dark" else (236, 236, 236)
DROPDOWN_HOVER_COLOR = (47, 47, 47) if THEME == "Dark" else (231, 231, 231)

TABS = ["Canvas", "File", "Settings"]
CANVAS_BOTTOM = None
CANVAS_RIGHT = None
CONTEXT_MENU_ITEMS = []
CONTEXT_MENU = [False, 0, 0]
RENDER_FRAME = True
CACHED_FRAME = None
POPUP_SHOW_VALUE = 1
LAST_POPUP = [None, 0, 0.5], 0
POPUP = [None, 0, 0.5]
DROPDOWNS = {}
SWITCHES = {}
FRAME = None
ITEMS = []
AREAS = []

AVAILABLE_LANGUAGES = {}
TRANSLATION_CACHE = {}
CUDA_AVAILABLE = False
CUDA_INSTALLED = False
CUDA_COMPATIBLE = False

FILE_PATH = None
CANVAS_CONTENT = []

CANVAS_POSITION = None, None
CANVAS_ZOOM = 1
CANVAS_SHOW_GRID = True
CANVAS_GRID_TYPE = "DOT"
CANVAS_TEMP = []
CANVAS_DELETE_LIST = []
CANVAS_DRAW_COLOR = (255, 255, 255)
HOVERING_CANVAS = False
CANVAS_CHANGED = False

TOOLBAR = None
TOOLBAR_HOVERED = False
TOOLBAR_WIDTH = None
TOOLBAR_HEIGHT = None
TOOLBAR_ROWS = None
TOOLBAR_COLUMNS = 3
TOOLBAR_PADDING = 10

SMOOTH_LINES = settings.Get("Draw", "SmoothLines", False)
UPSCALE_LINES = settings.Get("Draw", "UpscaleLines", True)
ANTI_ALIASING_LINES = settings.Get("Draw", "AntiAliasingLines", False)
SMOOTH_INTERPOLATION = settings.Get("Draw", "SmoothInterpolation", False)
MOUSE_SLOWDOWN = settings.Get("Draw", "MouseSlowdown", 1)

DEFAULT_MOUSE_SPEED = None