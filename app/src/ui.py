import src.uicomponents as uicomponents
import src.translate as translate
import src.variables as variables
import src.settings as settings
import src.console as console
import src.pytorch as pytorch
import src.updater as updater

import numpy as np
import subprocess
import ctypes
import mouse
import math
import time
import cv2

if variables.OS == "nt":
    from ctypes import windll, byref, sizeof, c_int
    import win32gui, win32con

def Initialize():
    WindowWidth = settings.Get("UI", "Width", 960)
    WindowHeight = settings.Get("UI", "Height", 540)
    WindowX = settings.Get("UI", "X", 0)
    WindowY = settings.Get("UI", "Y", 0)

    if WindowWidth < 50 or WindowHeight < 50:
        WindowWidth = 700
        WindowHeight = 400

    variables.BACKGROUND = np.zeros((WindowHeight, WindowWidth, 3), np.uint8)
    variables.BACKGROUND[:] = variables.BACKGROUND_COLOR
    if variables.TITLE_BAR_HEIGHT > 0:
        cv2.rectangle(variables.BACKGROUND, (0, 0), (WindowWidth - 1, variables.TITLE_BAR_HEIGHT - 1), variables.TAB_BAR_COLOR, -1)

    variables.CONTEXT_MENU_ITEMS = [
        {"Name": "Restart",
        "Function": lambda: {Restart(), setattr(variables, "CONTEXT_MENU", [False, 0, 0]), setattr(variables, "RENDER_FRAME", True)}},
        {"Name": "Close",
        "Function": lambda: {Close(), setattr(variables, "CONTEXT_MENU", [False, 0, 0]), setattr(variables, "RENDER_FRAME", True)}},
        {"Name": "Search for updates",
        "Function": lambda: {updater.CheckForUpdates(), setattr(variables, "CONTEXT_MENU", [False, 0, 0]), setattr(variables, "RENDER_FRAME", True)}}]

    cv2.namedWindow(variables.NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(variables.NAME, WindowWidth, WindowHeight)
    cv2.imshow(variables.NAME, variables.BACKGROUND)
    cv2.waitKey(1)

    if variables.OS == "nt":
        variables.HWND = win32gui.FindWindow(None, variables.NAME)
        if variables.TITLE_BAR_HEIGHT == 0:
            windll.dwmapi.DwmSetWindowAttribute(variables.HWND, 35, byref(c_int((variables.BACKGROUND_COLOR[0] << 16) | (variables.BACKGROUND_COLOR[1] << 8) | variables.BACKGROUND_COLOR[2])), sizeof(c_int))
        else:
            windll.dwmapi.DwmSetWindowAttribute(variables.HWND, 35, byref(c_int((variables.TAB_BAR_COLOR[0] << 16) | (variables.TAB_BAR_COLOR[1] << 8) | variables.TAB_BAR_COLOR[2])), sizeof(c_int))
        Icon = win32gui.LoadImage(None, f"{variables.PATH}app/assets/{'icon_dark' if variables.THEME == 'Dark' else 'icon_light'}.ico", win32con.IMAGE_ICON, 0, 0, win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE)
        win32gui.SendMessage(variables.HWND, win32con.WM_SETICON, win32con.ICON_SMALL, Icon)
        win32gui.SendMessage(variables.HWND, win32con.WM_SETICON, win32con.ICON_BIG, Icon)

    Update()

def Resize(WindowWidth, WindowHeight):
    variables.BACKGROUND = np.zeros((WindowHeight, WindowWidth, 3), np.uint8)
    variables.BACKGROUND[:] = variables.BACKGROUND_COLOR
    if variables.TITLE_BAR_HEIGHT > 0:
        cv2.rectangle(variables.BACKGROUND, (0, 0), (WindowWidth - 1, variables.TITLE_BAR_HEIGHT - 1), variables.TAB_BAR_COLOR, -1)
    variables.CANVAS_BOTTOM = WindowHeight - 1 - variables.TITLE_BAR_HEIGHT
    variables.CANVAS_RIGHT = WindowWidth - 1
    variables.RENDER_FRAME = True

def Restart():
    if variables.DEVMODE == True:
        subprocess.Popen(f"python {variables.PATH}app/main.py --dev", cwd=variables.PATH)
    else:
        subprocess.Popen(f"{variables.PATH}Start.bat", cwd=variables.PATH, creationflags=subprocess.CREATE_NEW_CONSOLE)
    Close()

def Close():
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
        if int(win32gui.IsIconic(variables.HWND)) == 1:
            cv2.imshow(variables.NAME, variables.CACHED_FRAME)
            cv2.waitKey(1)
            return
    try:
        _, _, WindowWidth, WindowHeight = cv2.getWindowImageRect(variables.NAME)
    except:
        Close()
        return
    variables.TITLE_BAR_HEIGHT = TitleBarHeight
    variables.BACKGROUND = np.zeros((WindowHeight, WindowWidth, 3), np.uint8)
    variables.BACKGROUND[:] = variables.BACKGROUND_COLOR
    if TitleBarHeight > 0:
        cv2.rectangle(variables.BACKGROUND, (0, 0), (WindowWidth - 1, variables.TITLE_BAR_HEIGHT - 1), variables.TAB_BAR_COLOR, -1)
    if variables.OS == "nt":
        if TitleBarHeight == 0:
            from ctypes import windll, byref, sizeof, c_int
            windll.dwmapi.DwmSetWindowAttribute(variables.HWND, 35, byref(c_int((variables.BACKGROUND_COLOR[0] << 16) | (variables.BACKGROUND_COLOR[1] << 8) | variables.BACKGROUND_COLOR[2])), sizeof(c_int))
        else:
            from ctypes import windll, byref, sizeof, c_int
            windll.dwmapi.DwmSetWindowAttribute(variables.HWND, 35, byref(c_int((variables.TAB_BAR_COLOR[0] << 16) | (variables.TAB_BAR_COLOR[1] << 8) | variables.TAB_BAR_COLOR[2])), sizeof(c_int))
    variables.CANVAS_BOTTOM = WindowHeight - 1 - variables.TITLE_BAR_HEIGHT
    variables.CANVAS_RIGHT = WindowWidth - 1
    variables.RENDER_FRAME = True

def Update():
    CurrentTime = time.time()

    if variables.OS == "nt":
        if int(win32gui.IsIconic(variables.HWND)) == 1:
            cv2.imshow(variables.NAME, variables.CACHED_FRAME)
            cv2.waitKey(1)
            return

    try:
        WindowX, WindowY, WindowWidth, WindowHeight = cv2.getWindowImageRect(variables.NAME)
        if (WindowX, WindowY, WindowWidth, WindowHeight) != (variables.X, variables.Y, variables.WIDTH, variables.HEIGHT):
            variables.X, variables.Y, variables.WIDTH, variables.HEIGHT = WindowX, WindowY, WindowWidth, WindowHeight
            Resize(WindowWidth, WindowHeight)
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
    except:
        Close()
        return

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
            "Y2": variables.CANVAS_BOTTOM - 90})

        variables.ITEMS.append({
            "Type": "Button",
            "Text": "Update",
            "Function": lambda: updater.Update(),
            "X1": variables.CANVAS_RIGHT / 2 + 10,
            "Y1": variables.CANVAS_BOTTOM - 70,
            "X2": variables.CANVAS_RIGHT - 20,
            "Y2": variables.CANVAS_BOTTOM - 20})

        variables.ITEMS.append({
            "Type": "Button",
            "Text": "Don't Update",
            "Function": lambda: {SetTitleBarHeight(50), setattr(variables, "PAGE", "Canvas")},
            "X1": 20,
            "Y1": variables.CANVAS_BOTTOM - 70,
            "X2": variables.CANVAS_RIGHT / 2 - 10,
            "Y2": variables.CANVAS_BOTTOM - 20})

    if variables.PAGE == "CUDA":
        if variables.CUDA_INSTALLED == False and variables.CUDA_AVAILABLE == False and variables.CUDA_COMPATIBLE == False:
            Message = "CUDA is not installed, not available and not compatible."
        elif variables.CUDA_INSTALLED == True and variables.CUDA_AVAILABLE == False and variables.CUDA_COMPATIBLE == False:
            Message = "CUDA is installed but not available and not compatible."
        elif variables.CUDA_INSTALLED == True and variables.CUDA_AVAILABLE == False and variables.CUDA_COMPATIBLE == True:
            Message = "CUDA is installed but not available,\nprobably because your NVIDIA GPU is not compatible."
        elif variables.CUDA_INSTALLED == False and variables.CUDA_AVAILABLE == False and variables.CUDA_COMPATIBLE == True:
            Message = "CUDA is not installed and not available, but it is compatible."
        elif variables.CUDA_INSTALLED == True and variables.CUDA_AVAILABLE == True and variables.CUDA_COMPATIBLE == True:
            Message = "CUDA is installed, available and compatible."
        else:
            Message = ""
        variables.ITEMS.append({
            "Type": "Label",
            "Text": f"{'CUDA is installed' if variables.CUDA_INSTALLED else 'CUDA is not installed'}\n{'CUDA is available' if variables.CUDA_AVAILABLE else 'CUDA is not available'}\n{'CUDA is compatible' if variables.CUDA_COMPATIBLE else 'CUDA is not compatible'}\n\nWhen CUDA is installed and available, the app will run AI models\non your NVIDIA GPU which will result in a significant speed increase.\n\n{Message}",
            "X1": 0,
            "Y1": 10,
            "X2": variables.CANVAS_RIGHT,
            "Y2": variables.CANVAS_BOTTOM - 90})

        if variables.CUDA_INSTALLED == False and variables.CUDA_COMPATIBLE == True:
            variables.ITEMS.append({
                "Type": "Button",
                "Text": "Install CUDA libraries (3GB)",
                "Function": lambda: {setattr(variables, "PAGE", "Canvas"), pytorch.InstallCUDA()},
                "X1": variables.CANVAS_RIGHT / 2 + 10,
                "Y1": variables.CANVAS_BOTTOM - 70,
                "X2": variables.CANVAS_RIGHT - 20,
                "Y2": variables.CANVAS_BOTTOM - 20})

            variables.ITEMS.append({
                "Type": "Button",
                "Text": "Keep running on CPU",
                "Function": lambda: {setattr(variables, "PAGE", "Canvas")},
                "X1": 20,
                "Y1": variables.CANVAS_BOTTOM - 70,
                "X2": variables.CANVAS_RIGHT / 2 - 10,
                "Y2": variables.CANVAS_BOTTOM - 20})
        elif variables.CUDA_INSTALLED == False and variables.CUDA_AVAILABLE == False and variables.CUDA_COMPATIBLE == False:
            variables.ITEMS.append({
                "Type": "Button",
                "Text": "Install CUDA libraries anyway (3GB)",
                "Function": lambda: {setattr(variables, "PAGE", "Canvas"), pytorch.InstallCUDA()},
                "X1": variables.CANVAS_RIGHT / 2 + 10,
                "Y1": variables.CANVAS_BOTTOM - 70,
                "X2": variables.CANVAS_RIGHT - 20,
                "Y2": variables.CANVAS_BOTTOM - 20})

            variables.ITEMS.append({
                "Type": "Button",
                "Text": "Keep running on CPU",
                "Function": lambda: {setattr(variables, "PAGE", "Canvas")},
                "X1": 20,
                "Y1": variables.CANVAS_BOTTOM - 70,
                "X2": variables.CANVAS_RIGHT / 2 - 10,
                "Y2": variables.CANVAS_BOTTOM - 20})
        elif variables.CUDA_INSTALLED == True and variables.CUDA_AVAILABLE == True and variables.CUDA_COMPATIBLE == True:
            variables.ITEMS.append({
                "Type": "Button",
                "Text": "Uninstall CUDA libraries",
                "Function": lambda: {setattr(variables, "PAGE", "Canvas"), pytorch.UninstallCUDA()},
                "X1": variables.CANVAS_RIGHT / 2 + 10,
                "Y1": variables.CANVAS_BOTTOM - 70,
                "X2": variables.CANVAS_RIGHT - 20,
                "Y2": variables.CANVAS_BOTTOM - 20})

            variables.ITEMS.append({
                "Type": "Button",
                "Text": "Keep running on GPU with CUDA",
                "Function": lambda: {setattr(variables, "PAGE", "Canvas")},
                "X1": 20,
                "Y1": variables.CANVAS_BOTTOM - 70,
                "X2": variables.CANVAS_RIGHT / 2 - 10,
                "Y2": variables.CANVAS_BOTTOM - 20})
        else:
            variables.ITEMS.append({
                "Type": "Button",
                "Text": "Uninstall CUDA libraries",
                "Function": lambda: {setattr(variables, "PAGE", "Canvas"), pytorch.UninstallCUDA()},
                "X1": variables.CANVAS_RIGHT / 2 + 10,
                "Y1": variables.CANVAS_BOTTOM - 70,
                "X2": variables.CANVAS_RIGHT - 20,
                "Y2": variables.CANVAS_BOTTOM - 20})

            variables.ITEMS.append({
                "Type": "Button",
                "Text": "Keep running on CPU with CUDA",
                "Function": lambda: {setattr(variables, "PAGE", "Canvas")},
                "X1": 20,
                "Y1": variables.CANVAS_BOTTOM - 70,
                "X2": variables.CANVAS_RIGHT / 2 - 10,
                "Y2": variables.CANVAS_BOTTOM - 20})

    if variables.PAGE == "Menu":
        ...

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
            "Function": lambda: setattr(variables, "PAGE", "CUDA"),
            "X1": 10,
            "Y1": 41,
            "X2": variables.CANVAS_RIGHT / 2 - 5,
            "Y2": 76})

        variables.ITEMS.append({
            "Type": "Dropdown",
            "Text": "Language",
            "Items": [Name for Name, _ in translate.GetAvailableLanguages().items()],
            "DefaultItem": 27,
            "Function": lambda: {
                translate.SaveCache(),
                settings.Set("UI", "Language", translate.GetAvailableLanguages()[[Name for Name, _ in translate.GetAvailableLanguages().items()][variables.DROPDOWNS["Language"][1]]]),
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
                settings.Set("UI", "Theme", ["Dark", "Light"][variables.DROPDOWNS["Theme"][1]]),
                Restart() if variables.THEME != settings.Get("UI", "Theme", "Dark") else None
                },
            "X1": variables.CANVAS_RIGHT / 2 + 5,
            "Y1": 86,
            "X2": variables.CANVAS_RIGHT - 10,
            "Y2": 121})

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

    for Area in variables.AREAS:
        if Area[0] != "Label":
            if (Area[1] <= MouseX * WindowWidth <= Area[3] and Area[2] <= MouseY * WindowHeight <= Area[4]) != Area[5]:
                Area = (Area[1], Area[2], Area[3], Area[4], not Area[5])
                variables.RENDER_FRAME = True

    if ForegroundWindow == False and variables.CACHED_FRAME is not None and variables.POPUP[0] == None:
        variables.RENDER_FRAME = False

    if variables.RENDER_FRAME or LastLeftClicked != LeftClicked:
        variables.RENDER_FRAME = False

        variables.ITEMS = sorted(variables.ITEMS, key=lambda x: ["Label-First-Render", "Button-First-Render", "Switch-First-Render", "Dropdown-First-Render",
                                                                 "Label", "Button", "Switch", "Dropdown",
                                                                 "Label-Last-Render", "Button-Last-Render", "Switch-Last-Render", "Dropdown-Last-Render"].index(x["Type"]))
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

    if LastRightClicked == True and RightClicked == False:
        variables.CONTEXT_MENU = [True, MouseX, MouseY]
        variables.RENDER_FRAME = True

    variables.ITEMS = []

    cv2.imshow(variables.NAME, variables.CACHED_FRAME)
    cv2.waitKey(1)