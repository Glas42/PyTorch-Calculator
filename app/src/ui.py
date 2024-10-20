import src.uicomponents as uicomponents
import src.translate as translate
import src.variables as variables
import src.settings as settings
import src.console as console
import src.pytorch as pytorch
import src.updater as updater
import src.canvas as canvas
import src.file as file

import SimpleWindow
import subprocess
import ctypes
import mouse
import numpy
import math
import time
import cv2


def Initialize():
    WindowWidth = settings.Get("UI", "Width", 960)
    WindowHeight = settings.Get("UI", "Height", 540)
    WindowX = settings.Get("UI", "X", 0)
    WindowY = settings.Get("UI", "Y", 0)

    if WindowWidth < 50 or WindowHeight < 50:
        WindowWidth = 700
        WindowHeight = 400

    variables.X = WindowX
    variables.Y = WindowY
    variables.WIDTH = WindowWidth
    variables.HEIGHT = WindowHeight

    variables.CANVAS_BOTTOM = WindowHeight - 1 - variables.TITLE_BAR_HEIGHT
    variables.CANVAS_RIGHT = WindowWidth - 1
    variables.CANVAS_POSITION = WindowWidth // 2, WindowHeight // 2

    variables.BACKGROUND = numpy.zeros((WindowHeight, WindowWidth, 3), numpy.uint8)
    variables.BACKGROUND[:] = variables.BACKGROUND_COLOR
    if variables.TITLE_BAR_HEIGHT > 0:
        cv2.rectangle(variables.BACKGROUND, (0, 0), (WindowWidth - 1, variables.TITLE_BAR_HEIGHT - 1), variables.TAB_BAR_COLOR, -1)

    variables.CANVAS = numpy.zeros((variables.CANVAS_BOTTOM + 1, variables.WIDTH, 3), numpy.uint8)
    variables.CANVAS[:] = variables.BACKGROUND_COLOR

    variables.CONTEXT_MENU_ITEMS = [
        {"Name": "Restart",
        "Function": lambda: {Restart(), setattr(variables, "CONTEXT_MENU", [False, 0, 0]), setattr(variables, "RENDER_FRAME", True)}},
        {"Name": "Close",
        "Function": lambda: {Close(), setattr(variables, "CONTEXT_MENU", [False, 0, 0]), setattr(variables, "RENDER_FRAME", True)}},
        {"Name": "Search for updates",
        "Function": lambda: {updater.CheckForUpdates(), setattr(variables, "CONTEXT_MENU", [False, 0, 0]), setattr(variables, "RENDER_FRAME", True)}}]

    SimpleWindow.Initialize(Name=variables.NAME, Size=(WindowWidth, WindowHeight), Position=(WindowX, WindowY), TitleBarColor=variables.TAB_BAR_COLOR, Resizable=True, TopMost=False, Undestroyable=False, Icon=f"{variables.PATH}app/assets/{'icon_dark' if variables.THEME == 'Dark' else 'icon_light'}.ico")

    Update()

def Resize(WindowX, WindowY, WindowWidth, WindowHeight):
    variables.X = WindowX
    variables.Y = WindowY
    variables.WIDTH = WindowWidth
    variables.HEIGHT = WindowHeight
    variables.BACKGROUND = numpy.zeros((WindowHeight, WindowWidth, 3), numpy.uint8)
    variables.BACKGROUND[:] = variables.BACKGROUND_COLOR
    if variables.TITLE_BAR_HEIGHT > 0:
        cv2.rectangle(variables.BACKGROUND, (0, 0), (WindowWidth - 1, variables.TITLE_BAR_HEIGHT - 1), variables.TAB_BAR_COLOR, -1)
    variables.CANVAS_BOTTOM = WindowHeight - 1 - variables.TITLE_BAR_HEIGHT
    variables.CANVAS_RIGHT = WindowWidth - 1
    variables.RENDER_FRAME = True
    if variables.DEVMODE == True:
        SimpleWindow.SetPosition("PyTorch-Calculator (Dev Mode)", (variables.X + variables.WIDTH + 5, variables.Y + variables.HEIGHT + 5))
    SimpleWindow.SetPosition("PyTorch-Calculator Detection", (variables.X + variables.WIDTH + 5, variables.Y))

def Restart():
    file.Save(Path=f"{variables.PATH}cache/LastSession.txt")
    if variables.DEVMODE == True:
        subprocess.Popen(f"python {variables.PATH}app/main.py --dev {variables.PATH}cache/LastSession.txt", cwd=variables.PATH)
    else:
        subprocess.Popen(f"{variables.PATH}Start.bat {variables.PATH}cache/LastSession.txt", cwd=variables.PATH, creationflags=subprocess.CREATE_NEW_CONSOLE)
    Close(SaveCanvas=False)

def Close(SaveCanvas=True, SaveTranslateCache=True):
    if SaveCanvas:
        file.Save(Path=f"{variables.PATH}cache/LastSession.txt")
    if SaveTranslateCache:
        translate.SaveCache()
    settings.Set("UI", "X", variables.X)
    settings.Set("UI", "Y", variables.Y)
    settings.Set("UI", "Width", variables.WIDTH)
    settings.Set("UI", "Height", variables.HEIGHT)
    console.RestoreConsole()
    console.CloseConsole()
    variables.BREAK = True

def SetTitleBarHeight(TitleBarHeight):
    if variables.OS == "nt":
        if SimpleWindow.GetMinimized(variables.NAME):
            SimpleWindow.Show(variables.NAME,variables.CACHED_FRAME)
            return
    WindowWidth, WindowHeight = SimpleWindow.GetSize(variables.NAME)
    variables.TITLE_BAR_HEIGHT = TitleBarHeight
    variables.BACKGROUND = numpy.zeros((WindowHeight, WindowWidth, 3), numpy.uint8)
    variables.BACKGROUND[:] = variables.BACKGROUND_COLOR
    if TitleBarHeight > 0:
        cv2.rectangle(variables.BACKGROUND, (0, 0), (WindowWidth - 1, variables.TITLE_BAR_HEIGHT - 1), variables.TAB_BAR_COLOR, -1)
    if variables.OS == "nt":
        if TitleBarHeight == 0:
            SimpleWindow.SetTitleBarColor(variables.NAME, variables.BACKGROUND_COLOR)
        else:
            SimpleWindow.SetTitleBarColor(variables.NAME, variables.TAB_BAR_COLOR)
    variables.CANVAS_BOTTOM = WindowHeight - 1 - variables.TITLE_BAR_HEIGHT
    variables.CANVAS_RIGHT = WindowWidth - 1
    variables.RENDER_FRAME = True

def Update():
    CurrentTime = time.time()

    if variables.OS == "nt":
        if SimpleWindow.GetMinimized(variables.NAME):
            SimpleWindow.Show(variables.NAME, variables.CACHED_FRAME)
            return

    if SimpleWindow.GetOpen(variables.NAME) == None:
        Close()

    WindowX, WindowY = SimpleWindow.GetPosition(variables.NAME)
    WindowWidth, WindowHeight = SimpleWindow.GetSize(variables.NAME)
    if (WindowX, WindowY, WindowWidth, WindowHeight) != (variables.X, variables.Y, variables.WIDTH, variables.HEIGHT):
        variables.X, variables.Y, variables.WIDTH, variables.HEIGHT = WindowX, WindowY, WindowWidth, WindowHeight
        Resize(WindowX, WindowY, WindowWidth, WindowHeight)
    MouseX, MouseY = mouse.get_position()
    MouseRelativeWindow = MouseX - WindowX, MouseY - WindowY
    if WindowWidth != 0 and WindowHeight != 0:
        MouseX = MouseRelativeWindow[0]/WindowWidth
        MouseY = MouseRelativeWindow[1]/WindowHeight
    else:
        MouseX = 0
        MouseY = 0
    LastLeftClicked = uicomponents.LeftClicked
    LastRightClicked = uicomponents.RightClicked
    ForegroundWindow = ctypes.windll.user32.GetForegroundWindow() == ctypes.windll.user32.FindWindowW(None, variables.NAME)
    LeftClicked = ctypes.windll.user32.GetKeyState(0x01) & 0x8000 != 0 and ForegroundWindow
    RightClicked = ctypes.windll.user32.GetKeyState(0x02) & 0x8000 != 0 and ForegroundWindow
    uicomponents.ForegroundWindow = ForegroundWindow
    uicomponents.FrameWidth = WindowWidth
    uicomponents.FrameHeight = WindowHeight
    uicomponents.MouseX = MouseX
    uicomponents.MouseY = MouseY
    uicomponents.LastLeftClicked = uicomponents.LeftClicked
    uicomponents.LastRightClicked = uicomponents.RightClicked
    uicomponents.LeftClicked = LeftClicked
    uicomponents.RightClicked = RightClicked


    if variables.TITLE_BAR_HEIGHT > 0:
        for i, Tab in enumerate(variables.TABS):
            variables.ITEMS.append({
                "Type": "Button-Last-Render",
                "Text": Tab,
                "Function": lambda Tab = Tab: {setattr(variables, "PAGE", Tab), settings.Set("UI", "Page", Tab)},
                "X1": i / len(variables.TABS) * variables.CANVAS_RIGHT + 5,
                "Y1": -variables.TITLE_BAR_HEIGHT + 6,
                "X2": (i + 1) / len(variables.TABS) * variables.CANVAS_RIGHT - 5,
                "Y2": -6,
                "ButtonSelected": variables.PAGE == Tab,
                "ButtonColor": variables.TAB_BUTTON_COLOR,
                "ButtonHoverColor": variables.TAB_BUTTON_HOVER_COLOR,
                "ButtonSelectedColor": variables.TAB_BUTTON_SELECTED_COLOR,
                "ButtonSelectedHoverColor": variables.TAB_BUTTON_SELECTED_HOVER_COLOR})

    if variables.PAGE == "Update":
        variables.ITEMS.append({
            "Type": "Label",
            "Text": f"Update Available:\n{variables.VERSION} -> {variables.REMOTE_VERSION}",
            "X1": 0,
            "Y1": 10,
            "X2": variables.CANVAS_RIGHT,
            "Y2": 50})

        variables.ITEMS.append({
            "Type": "Label",
            "Text": f"Changelog:\n\n{variables.CHANGELOG}\n\n",
            "X1": 0,
            "Y1": 60,
            "X2": variables.CANVAS_RIGHT,
            "Y2": variables.CANVAS_BOTTOM - 80})

        variables.ITEMS.append({
            "Type": "Button",
            "Text": "Update",
            "Function": lambda: updater.Update(),
            "X1": variables.CANVAS_RIGHT / 2 + 5,
            "Y1": variables.CANVAS_BOTTOM - 60,
            "X2": variables.CANVAS_RIGHT - 10,
            "Y2": variables.CANVAS_BOTTOM - 10})

        variables.ITEMS.append({
            "Type": "Button",
            "Text": "Don't Update",
            "Function": lambda: {SetTitleBarHeight(50), setattr(variables, "PAGE", "Canvas")},
            "X1": 10,
            "Y1": variables.CANVAS_BOTTOM - 60,
            "X2": variables.CANVAS_RIGHT / 2 - 5,
            "Y2": variables.CANVAS_BOTTOM - 10})

    if variables.PAGE == "CUDA":
        if variables.CUDA_INSTALLED != "Loading..." and variables.CUDA_AVAILABLE != "Loading..." and variables.CUDA_COMPATIBLE != "Loading..." and variables.CUDA_DETAILS != "Loading...":
            if variables.CUDA_INSTALLED == False and variables.CUDA_AVAILABLE == False and variables.CUDA_COMPATIBLE == False:
                Message = "CUDA is not installed, not available and not compatible."
            elif variables.CUDA_INSTALLED == True and variables.CUDA_AVAILABLE == False and variables.CUDA_COMPATIBLE == False:
                Message = "CUDA is installed but not available and not compatible."
            elif variables.CUDA_INSTALLED == True and variables.CUDA_AVAILABLE == False and variables.CUDA_COMPATIBLE == True:
                Message = "CUDA is installed but not available, probably because your NVIDIA GPU is not compatible."
            elif variables.CUDA_INSTALLED == False and variables.CUDA_AVAILABLE == False and variables.CUDA_COMPATIBLE == True:
                Message = "CUDA is not installed and not available, but it is compatible."
            elif variables.CUDA_INSTALLED == False and variables.CUDA_AVAILABLE == True and variables.CUDA_COMPATIBLE == True:
                Message = "CUDA is not installed but available and compatible,\nprobably because Python is using a CUDA installation outside of the app environment."
            elif variables.CUDA_INSTALLED == True and variables.CUDA_AVAILABLE == True and variables.CUDA_COMPATIBLE == True:
                Message = "CUDA is installed, available and compatible."
            else:
                Message = f"INSTALLED: {variables.CUDA_INSTALLED} AVAILABLE: {variables.CUDA_AVAILABLE} COMPATIBLE: {variables.CUDA_COMPATIBLE}"
            variables.ITEMS.append({
                "Type": "Label",
                "Text": "When CUDA is installed and available, the app will run AI models\non your NVIDIA GPU which will result in a significant speed increase.",
                "X1": 10,
                "Y1": 10,
                "X2": variables.CANVAS_RIGHT - 10,
                "Y2": 60})

            variables.ITEMS.append({
                "Type": "Label",
                "Text": f"{Message}",
                "X1": 10,
                "Y1": 80,
                "X2": variables.CANVAS_RIGHT - 10,
                "Y2": 130})

            variables.ITEMS.append({
                "Type": "Label",
                "Text": f"Details:\n{variables.CUDA_DETAILS}",
                "X1": 10,
                "Y1": 150,
                "X2": variables.CANVAS_RIGHT - 10,
                "Y2": 275})

            if variables.CUDA_INSTALLED == False and variables.CUDA_COMPATIBLE == True:
                variables.ITEMS.append({
                    "Type": "Button",
                    "Text": "Install CUDA libraries (3GB)",
                    "Function": lambda: {setattr(variables, "PAGE", "Canvas"), pytorch.InstallCUDA()},
                    "X1": variables.CANVAS_RIGHT / 2 + 5,
                    "Y1": variables.CANVAS_BOTTOM - 60,
                    "X2": variables.CANVAS_RIGHT - 10,
                    "Y2": variables.CANVAS_BOTTOM - 10})

                variables.ITEMS.append({
                    "Type": "Button",
                    "Text": "Keep running on CPU",
                    "Function": lambda: {setattr(variables, "PAGE", "Canvas")},
                    "X1": 10,
                    "Y1": variables.CANVAS_BOTTOM - 60,
                    "X2": variables.CANVAS_RIGHT / 2 - 5,
                    "Y2": variables.CANVAS_BOTTOM - 10})
            elif variables.CUDA_INSTALLED == False and variables.CUDA_AVAILABLE == False and variables.CUDA_COMPATIBLE == False:
                variables.ITEMS.append({
                    "Type": "Button",
                    "Text": "Install CUDA libraries anyway (3GB)",
                    "Function": lambda: {setattr(variables, "PAGE", "Canvas"), pytorch.InstallCUDA()},
                    "X1": variables.CANVAS_RIGHT / 2 + 5,
                    "Y1": variables.CANVAS_BOTTOM - 60,
                    "X2": variables.CANVAS_RIGHT - 10,
                    "Y2": variables.CANVAS_BOTTOM - 10})

                variables.ITEMS.append({
                    "Type": "Button",
                    "Text": "Keep running on CPU",
                    "Function": lambda: {setattr(variables, "PAGE", "Canvas")},
                    "X1": 10,
                    "Y1": variables.CANVAS_BOTTOM - 60,
                    "X2": variables.CANVAS_RIGHT / 2 - 5,
                    "Y2": variables.CANVAS_BOTTOM - 10})
            elif variables.CUDA_INSTALLED == True and variables.CUDA_AVAILABLE == True and variables.CUDA_COMPATIBLE == True:
                variables.ITEMS.append({
                    "Type": "Button",
                    "Text": "Uninstall CUDA libraries",
                    "Function": lambda: {setattr(variables, "PAGE", "Canvas"), pytorch.UninstallCUDA()},
                    "X1": variables.CANVAS_RIGHT / 2 + 5,
                    "Y1": variables.CANVAS_BOTTOM - 60,
                    "X2": variables.CANVAS_RIGHT - 10,
                    "Y2": variables.CANVAS_BOTTOM - 10})

                variables.ITEMS.append({
                    "Type": "Button",
                    "Text": "Keep running on GPU with CUDA",
                    "Function": lambda: {setattr(variables, "PAGE", "Canvas")},
                    "X1": 10,
                    "Y1": variables.CANVAS_BOTTOM - 60,
                    "X2": variables.CANVAS_RIGHT / 2 - 5,
                    "Y2": variables.CANVAS_BOTTOM - 10})
            else:
                variables.ITEMS.append({
                    "Type": "Button",
                    "Text": "Uninstall CUDA libraries",
                    "Function": lambda: {setattr(variables, "PAGE", "Canvas"), pytorch.UninstallCUDA()},
                    "X1": variables.CANVAS_RIGHT / 2 + 5,
                    "Y1": variables.CANVAS_BOTTOM - 60,
                    "X2": variables.CANVAS_RIGHT - 10,
                    "Y2": variables.CANVAS_BOTTOM - 10})

                variables.ITEMS.append({
                    "Type": "Button",
                    "Text": "Keep running on CPU with CUDA",
                    "Function": lambda: {setattr(variables, "PAGE", "Canvas")},
                    "X1": 10,
                    "Y1": variables.CANVAS_BOTTOM - 60,
                    "X2": variables.CANVAS_RIGHT / 2 - 5,
                    "Y2": variables.CANVAS_BOTTOM - 10})
        else:
            variables.RENDER_FRAME = True
            variables.ITEMS.append({
                "Type": "Label",
                "Text": f"Checking your CUDA compatibility, please wait...",
                "X1": 10,
                "Y1": 10,
                "X2": variables.CANVAS_RIGHT - 10,
                "Y2": variables.CANVAS_BOTTOM - 10})

    if variables.PAGE == "Canvas":
        variables.ITEMS.append({
            "Type": "Image",
            "Image": canvas.Frame,
            "X1": 0,
            "Y1": 0,
            "X2": variables.CANVAS_RIGHT,
            "Y2": variables.CANVAS_BOTTOM})

    if variables.PAGE == "File":
        variables.ITEMS.append({
            "Type": "Switch",
            "Text": "Smooth Lines",
            "State": variables.SMOOTH_LINES,
            "Function": lambda: {setattr(variables, "SMOOTH_LINES", not variables.SMOOTH_LINES), print("hello from func"), setattr(variables, "RENDER_FRAME", True)},
            "X1": 10,
            "Y1": 11,
            "X2": variables.CANVAS_RIGHT - 10,
            "Y2": 31})

        variables.ITEMS.append({
            "Type": "Switch",
            "Text": "Upscale Lines",
            "State": variables.UPSCALE_LINES,
            "Function": lambda: {setattr(variables, "UPSCALE_LINES", not variables.UPSCALE_LINES), setattr(variables, "RENDER_FRAME", True)},
            "X1": 10,
            "Y1": 41,
            "X2": variables.CANVAS_RIGHT - 10,
            "Y2": 61})

        variables.ITEMS.append({
            "Type": "Switch",
            "Text": "Anti-Aliasing Lines",
            "State": variables.ANTI_ALIASING_LINES,
            "Function": lambda: {setattr(variables, "ANTI_ALIASING_LINES", not variables.ANTI_ALIASING_LINES), setattr(variables, "RENDER_FRAME", True)},
            "X1": 10,
            "Y1": 71,
            "X2": variables.CANVAS_RIGHT - 10,
            "Y2": 91})

        variables.ITEMS.append({
            "Type": "Switch",
            "Text": "Smooth Interpolation",
            "State": variables.SMOOTH_INTERPOLATION,
            "Function": lambda: {setattr(variables, "SMOOTH_INTERPOLATION", not variables.SMOOTH_INTERPOLATION), setattr(variables, "RENDER_FRAME", True)},
            "X1": 10,
            "Y1": 101,
            "X2": variables.CANVAS_RIGHT - 10,
            "Y2": 121})

        variables.ITEMS.append({
            "Type": "Button",
            "Text": "Save",
            "Function": lambda: {file.Save(Path=variables.FILE_PATH)},
            "X1": 10,
            "Y1": 131,
            "X2": variables.CANVAS_RIGHT / 2 - 5,
            "Y2": 166})

        variables.ITEMS.append({
            "Type": "Button",
            "Text": "Save as...",
            "Function": lambda: {file.Save()},
            "X1": variables.CANVAS_RIGHT / 2 + 5,
            "Y1": 131,
            "X2": variables.CANVAS_RIGHT - 10,
            "Y2": 166})

        variables.ITEMS.append({
            "Type": "Button",
            "Text": "Open",
            "Function": lambda: {file.Open()},
            "X1": 10,
            "Y1": 176,
            "X2": variables.CANVAS_RIGHT / 2 - 5,
            "Y2": 211})

        variables.ITEMS.append({
            "Type": "Button",
            "Text": "New",
            "Function": lambda: {file.New()},
            "X1": variables.CANVAS_RIGHT / 2 + 5,
            "Y1": 176,
            "X2": variables.CANVAS_RIGHT - 10,
            "Y2": 211})

    if variables.PAGE == "Settings":
        variables.ITEMS.append({
            "Type": "Switch",
            "Text": "Hide Console",
            "Setting": ("Console", "HideConsole", False),
            "Function": lambda: {console.HideConsole() if settings.Get("Console", "HideConsole", False) else console.RestoreConsole()},
            "X1": 10,
            "Y1": 11,
            "X2": variables.CANVAS_RIGHT - 10,
            "Y2": 31})

        variables.ITEMS.append({
            "Type": "Button",
            "Text": "Check Cuda (GPU) Support",
            "Function": lambda: {pytorch.CheckCuda(), setattr(variables, "PAGE", "CUDA")},
            "X1": 10,
            "Y1": 41,
            "X2": variables.CANVAS_RIGHT / 2 - 5,
            "Y2": 76})

        variables.ITEMS.append({
            "Type": "Button",
            "Text": "Restart App in Dev Mode" if variables.DEVMODE == False else "Restart App in Normal Mode",
            "Function": lambda: {
                file.Save(Path=f"{variables.PATH}cache/LastSession.txt"),
                subprocess.Popen(f"{variables.PATH}Start.bat --dev {variables.PATH}cache/LastSession.txt" if variables.DEVMODE == False else f"{variables.PATH}Start.bat {variables.PATH}cache/LastSession.txt", cwd=variables.PATH, creationflags=subprocess.CREATE_NEW_CONSOLE),
                Close(SaveCanvas=False)},
            "X1": variables.CANVAS_RIGHT / 2 + 5,
            "Y1": 41,
            "X2": variables.CANVAS_RIGHT - 10,
            "Y2": 76})

        variables.ITEMS.append({
            "Type": "Dropdown",
            "Text": "Language",
            "Items": [Name for Name, _ in translate.GetAvailableLanguages().items()],
            "DefaultItem": 27,
            "Function": lambda: {
                translate.SaveCache(),
                settings.Set("UI", "Language", translate.GetAvailableLanguages()[[Name for Name, _ in translate.GetAvailableLanguages().items()][variables.DROPDOWNS["Language" + str([Name for Name, _ in translate.GetAvailableLanguages().items()])][1]]]),
                setattr(variables, "LANGUAGE", settings.Get("UI", "Language", "en")),
                setattr(variables, "TRANSLATION_CACHE", {}),
                setattr(variables, "RENDER_FRAME", True),
                translate.Initialize()
                },
            "X1": 10,
            "Y1": 86,
            "X2": variables.CANVAS_RIGHT / 2 - 5,
            "Y2": 121})

        variables.ITEMS.append({
            "Type": "Dropdown",
            "Text": "Theme",
            "Items": ["Dark", "Light"],
            "DefaultItem": 0,
            "Function": lambda: {
                settings.Set("UI", "Theme", ["Dark", "Light"][variables.DROPDOWNS["Theme" + str(["Dark", "Light"])][1]]),
                Restart() if variables.THEME != settings.Get("UI", "Theme", "Dark") else None
                },
            "X1": variables.CANVAS_RIGHT / 2 + 5,
            "Y1": 86,
            "X2": variables.CANVAS_RIGHT - 10,
            "Y2": 121})

        variables.ITEMS.append({
            "Type": "Switch",
            "Text": "Smooth Lines",
            "Setting": ("Draw", "SmoothLines", False),
            "Function": lambda: {setattr(variables, "RENDER_FRAME", True)},
            "X1": 10,
            "Y1": 151,
            "X2": variables.CANVAS_RIGHT - 10,
            "Y2": 171})

        variables.ITEMS.append({
            "Type": "Switch",
            "Text": "Upscale Lines",
            "Setting": ("Draw", "UpscaleLines", True),
            "Function": lambda: {setattr(variables, "RENDER_FRAME", True)},
            "X1": 10,
            "Y1": 181,
            "X2": variables.CANVAS_RIGHT - 10,
            "Y2": 201})

        variables.ITEMS.append({
            "Type": "Switch",
            "Text": "Anti-Aliasing Lines",
            "Setting": ("Draw", "AntiAliasingLines", True),
            "Function": lambda: {setattr(variables, "RENDER_FRAME", True)},
            "X1": 10,
            "Y1": 211,
            "X2": variables.CANVAS_RIGHT - 10,
            "Y2": 231})

        variables.ITEMS.append({
            "Type": "Switch",
            "Text": "Smooth Interpolation",
            "Setting": ("Draw", "SmoothInterpolation", False),
            "Function": lambda: {setattr(variables, "RENDER_FRAME", True)},
            "X1": 10,
            "Y1": 241,
            "X2": variables.CANVAS_RIGHT - 10,
            "Y2": 261})

        variables.ITEMS.append({
            "Type": "Button",
            "Text": "Apply Global Canvas Settings to Current File",
            "Function": lambda: {
                setattr(variables, "SMOOTH_LINES", settings.Get("Draw", "SmoothLines", False)),
                setattr(variables, "UPSCALE_LINES", settings.Get("Draw", "UpscaleLines", True)),
                setattr(variables, "ANTI_ALIASING_LINES", settings.Get("Draw", "AntiAliasingLines", True)),
                setattr(variables, "SMOOTH_INTERPOLATION", settings.Get("Draw", "SmoothInterpolation", False)),
                setattr(variables, "DROPDOWNS", {}),
                setattr(variables, "SWITCHES", {}),
                setattr(variables, "PAGE", "File"),
                setattr(variables, "POPUP", ["Applied Global Canvas Settings to Current File", 0, 0.5])},
            "X1": 10,
            "Y1": 271,
            "X2": variables.CANVAS_RIGHT / 2 - 5,
            "Y2": 306})

    if variables.CONTEXT_MENU[0]:
        Offset = 0
        for Item in variables.CONTEXT_MENU_ITEMS:
            variables.ITEMS.append({
                "Type": "Button-Last-Render",
                "Text": Item["Name"],
                "Function": Item["Function"],
                "X1": variables.CONTEXT_MENU[1] * variables.CANVAS_RIGHT,
                "Y1": variables.CONTEXT_MENU[2] * (variables.CANVAS_BOTTOM + variables.TITLE_BAR_HEIGHT) - variables.TITLE_BAR_HEIGHT + Offset,
                "X2": variables.CONTEXT_MENU[1] * variables.CANVAS_RIGHT + 200,
                "Y2": variables.CONTEXT_MENU[2] * (variables.CANVAS_BOTTOM + variables.TITLE_BAR_HEIGHT) - variables.TITLE_BAR_HEIGHT + Offset + 30})
            Offset += 35

    if variables.LAST_POPUP[0] != variables.POPUP or variables.POPUP[1] != 0:
        if variables.LAST_POPUP[0][0] == None:
            variables.LAST_POPUP = variables.POPUP, CurrentTime
            variables.POPUP_SHOW_VALUE = 1
        else:
            variables.LAST_POPUP = variables.POPUP, CurrentTime - 1
            variables.POPUP_SHOW_VALUE = 0
        variables.RENDER_FRAME = True
    elif variables.POPUP[0] != None and variables.LAST_POPUP[1] + 5 < CurrentTime:
        variables.POPUP = [None, 0, 0.5]
        variables.LAST_POPUP = [None, 0, 0.5], 0
        variables.POPUP_SHOW_VALUE = 1
        variables.RENDER_FRAME = True
    elif variables.POPUP[0] != None and variables.LAST_POPUP[1] + 4.5 < CurrentTime:
        variables.POPUP_SHOW_VALUE = -(math.cos(math.pi * ((CurrentTime - variables.LAST_POPUP[1] - 4.5) * 2)) - 1) / 2
        variables.RENDER_FRAME = True
    elif variables.LAST_POPUP[1] + 0.5 > CurrentTime:
        variables.POPUP_SHOW_VALUE = math.pow(2, 10 * (1 - (CurrentTime - variables.LAST_POPUP[1]) * 2) - 10)
        variables.RENDER_FRAME = True

    if variables.HOVERING_CANVAS == True and variables.CANVAS_CHANGED == True:
        variables.CANVAS_CHANGED = False
        variables.RENDER_FRAME = True

    for Area in variables.AREAS:
        if Area[0] != "Label":
            if (Area[1] <= MouseX * WindowWidth <= Area[3] and Area[2] <= MouseY * WindowHeight <= Area[4]) != Area[5]:
                Area = (Area[1], Area[2], Area[3], Area[4], not Area[5])
                variables.RENDER_FRAME = True

    if ForegroundWindow == False and variables.CACHED_FRAME is not None and variables.POPUP[0] == None:
        variables.RENDER_FRAME = False

    if variables.RENDER_FRAME or LastLeftClicked != LeftClicked:
        variables.RENDER_FRAME = False

        variables.ITEMS = sorted(variables.ITEMS, key=lambda x: ["Label-First-Render", "Button-First-Render", "Switch-First-Render", "Dropdown-First-Render", "Image-First-Render", "Images-First-Render",
                                                                 "Label", "Button", "Switch", "Dropdown", "Image", "Images",
                                                                 "Label-Last-Render", "Button-Last-Render", "Switch-Last-Render", "Dropdown-Last-Render", "Image-Last-Render", "Images-Last-Render"].index(x["Type"]))
        variables.FRAME = variables.BACKGROUND.copy()
        variables.AREAS = []

        for Item in variables.ITEMS:
            ItemType = Item["Type"].split("-")[0]
            Item.pop("Type")
            ItemFunction = None
            if "Function" in Item:
                ItemFunction = Item["Function"]
                Item.pop("Function")

            if ItemType == "Label":
                uicomponents.Label(**Item)

            elif ItemType == "Button":
                Changed, Pressed, Hovered = uicomponents.Button(**Item)
                variables.AREAS.append((ItemType, Item["X1"], Item["Y1"] + variables.TITLE_BAR_HEIGHT, Item["X2"], Item["Y2"] + variables.TITLE_BAR_HEIGHT, Pressed or Hovered))

                if Changed:
                    if ItemFunction is not None:
                        ItemFunction()
                    else:
                        variables.RENDER_FRAME = True

            elif ItemType == "Switch":
                Changed, Pressed, Hovered = uicomponents.Switch(**Item)
                variables.AREAS.append((ItemType, Item["X1"], Item["Y1"] + variables.TITLE_BAR_HEIGHT, Item["X2"], Item["Y2"] + variables.TITLE_BAR_HEIGHT, Pressed or Hovered))

                if Changed:
                    if ItemFunction is not None:
                        ItemFunction()

            elif ItemType == "Dropdown":
                Changed, Pressed, Hovered = uicomponents.Dropdown(**Item)
                variables.AREAS.append((ItemType, Item["X1"], Item["Y1"] + variables.TITLE_BAR_HEIGHT, Item["X2"], Item["Y2"] + variables.TITLE_BAR_HEIGHT, Pressed or Hovered))

                if Changed:
                    if ItemFunction is not None:
                        ItemFunction()

            elif ItemType == "Image":
                uicomponents.Image(**Item)

            elif ItemType == "Images":
                uicomponents.Images(**Item)

        if len(variables.ITEMS) < len(variables.TABS) + 1 and variables.TITLE_BAR_HEIGHT != 0:
            uicomponents.Label(
                Text="\n\nYou landed on an empty page...\nPlease report how you got here!\n\n",
                X1=0,
                Y1=0,
                X2=variables.CANVAS_RIGHT - 1,
                Y2=variables.CANVAS_BOTTOM)

        if variables.POPUP[0] != None:
            if variables.POPUP_SHOW_VALUE < 0.01:
                variables.POPUP_SHOW_VALUE = 0
            elif variables.POPUP_SHOW_VALUE > 0.99:
                variables.POPUP_SHOW_VALUE = 1
            X1 = variables.CANVAS_RIGHT * (0.5 - variables.POPUP[2] / 2)
            Y1 = variables.CANVAS_BOTTOM - variables.POPUP_HEIGHT + variables.POPUP_HEIGHT * variables.POPUP_SHOW_VALUE
            X2 = variables.CANVAS_RIGHT * (0.5 + variables.POPUP[2] / 2)
            Y2 = variables.CANVAS_BOTTOM - variables.POPUP_HEIGHT * 0.25 + variables.POPUP_HEIGHT * variables.POPUP_SHOW_VALUE
            uicomponents.Button(
                Text=str(variables.POPUP[0]),
                X1=X1,
                Y1=Y1,
                X2=X2,
                Y2=Y2,
                ButtonColor=variables.POPUP_COLOR,
                ButtonHoverColor=variables.POPUP_HOVER_COLOR)
            if variables.POPUP[1] > 0:
                cv2.line(variables.FRAME,
                        (round(X1 + round(variables.POPUP_HEIGHT / 20) / 2), round(variables.POPUP_HEIGHT + Y2 + variables.POPUP_HEIGHT / 40)),
                        (round(X1 - round(variables.POPUP_HEIGHT / 20) / 2 + variables.CANVAS_RIGHT * variables.POPUP[2] * (variables.POPUP[1] / 100)), round(variables.POPUP_HEIGHT + Y2 + variables.POPUP_HEIGHT / 40)),
                        variables.POPUP_PROGRESS_COLOR, round(variables.POPUP_HEIGHT / 20))
            elif variables.POPUP[1] < 0:
                X = time.time() % 2
                if X < 1:
                    Left = 0.5 - math.cos(X ** 2 * math.pi) / 2
                    Right = 0.5 - math.cos((X + (X - X ** 2)) * math.pi) / 2
                else:
                    X -= 1
                    Left = 0.5 + math.cos((X + (X - X ** 2)) * math.pi) / 2
                    Right = 0.5 + math.cos(X ** 2 * math.pi) / 2
                cv2.line(variables.FRAME,
                        (round(X1 + round(variables.POPUP_HEIGHT / 20) / 2 + variables.CANVAS_RIGHT * variables.POPUP[2] * Left), round(variables.POPUP_HEIGHT + Y2 + variables.POPUP_HEIGHT / 40)),
                        (round(X1 - round(variables.POPUP_HEIGHT / 20) / 2 + variables.CANVAS_RIGHT * variables.POPUP[2] * Right), round(variables.POPUP_HEIGHT + Y2 + variables.POPUP_HEIGHT / 40)),
                        variables.POPUP_PROGRESS_COLOR, round(variables.POPUP_HEIGHT / 20))

        variables.CACHED_FRAME = variables.FRAME.copy()

        if LastLeftClicked == True and LeftClicked == False:
            variables.CONTEXT_MENU = [False, MouseX, MouseY]
            variables.RENDER_FRAME = True

    if LastRightClicked == True and RightClicked == False and variables.HOVERING_CANVAS == False:
        variables.CONTEXT_MENU = [True, MouseX, MouseY]
        variables.RENDER_FRAME = True

    variables.ITEMS = []

    SimpleWindow.Show(variables.NAME, variables.CACHED_FRAME)