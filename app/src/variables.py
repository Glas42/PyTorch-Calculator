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

AVAILABLE_LANGUAGES = {}
TRANSLATION_CACHE = {}
CUDA_AVAILABLE = False
CUDA_INSTALLED = False
CUDA_COMPATIBLE = False

TABS = ["Canvas", "File", "Settings"]
CANVAS_BOTTOM = settings.Get("UI", "Height", 540) - TITLE_BAR_HEIGHT - 1
CANVAS_RIGHT = settings.Get("UI", "Width", 960) - 1
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

X = settings.Get("UI", "X", 0)
Y = settings.Get("UI", "Y", 0)
WIDTH = settings.Get("UI", "Width", 960)
HEIGHT = settings.Get("UI", "Height", 540)

HWND = None
NAME = "PyTorch-Calculator"
PAGE = settings.Get("UI", "PAGE", "Canvas")
BREAK = False

CONSOLENAME = None
CONSOLEHWND = None