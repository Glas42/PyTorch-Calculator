import src.uicomponents as uicomponents
import src.translate as translate
import src.variables as variables
import src.settings as settings
import src.console as console
import src.pytorch as pytorch
import src.updater as updater
import src.canvas as canvas
import src.window as window

import subprocess
import ctypes
import mouse
import numpy
import math
import time
import cv2
import os


def Initialize():
    WindowWidth = settings.Get("UI", "Width", 960)
    WindowHeight = settings.Get("UI", "Height", 540)
    WindowX = settings.Get("UI", "X", 0)
    WindowY = settings.Get("UI", "Y", 0)

    if WindowWidth < 50 or WindowHeight < 50:
        WindowWidth = 700
        WindowHeight = 400

    variables.WIDTH = WindowWidth
    variables.HEIGHT = WindowHeight
    variables.X = WindowX
    variables.Y = WindowY

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

    window.Initialize(Name=variables.NAME, Size=(WindowWidth, WindowHeight), Position=(WindowX, WindowY), TitleBarColor=variables.TAB_BAR_COLOR, Resizable=True, TopMost=False, Undestroyable=False, Icon=f"{variables.PATH}app/assets/{'icon_dark' if variables.THEME == 'Dark' else 'icon_light'}.ico")

    LoadToolBar()
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
        if window.GetWindowStatus(variables.NAME)["Iconic"]:
            window.Show(variables.NAME,variables.CACHED_FRAME)
            return
    WindowWidth, WindowHeight = window.GetWindowSize(variables.NAME)
    variables.TITLE_BAR_HEIGHT = TitleBarHeight
    variables.BACKGROUND = numpy.zeros((WindowHeight, WindowWidth, 3), numpy.uint8)
    variables.BACKGROUND[:] = variables.BACKGROUND_COLOR
    if TitleBarHeight > 0:
        cv2.rectangle(variables.BACKGROUND, (0, 0), (WindowWidth - 1, variables.TITLE_BAR_HEIGHT - 1), variables.TAB_BAR_COLOR, -1)
    if variables.OS == "nt":
        if TitleBarHeight == 0:
            window.SetTitleBarColor(variables.NAME, variables.BACKGROUND_COLOR)
        else:
            window.SetTitleBarColor(variables.NAME, variables.TAB_BAR_COLOR)
    variables.CANVAS_BOTTOM = WindowHeight - 1 - variables.TITLE_BAR_HEIGHT
    variables.CANVAS_RIGHT = WindowWidth - 1
    variables.RENDER_FRAME = True

def LoadToolBar():
    global tools_icon
    global tools_placeholder
    tools_icon = cv2.resize(cv2.imread(f'{variables.PATH}app/assets/pen_{variables.THEME.lower()}.png', cv2.IMREAD_UNCHANGED), (20, 20))
    for x in range(tools_icon.shape[1]):
        for y in range(tools_icon.shape[0]):
            if tools_icon[x][y][3] == 0:
                tools_icon[x][y] = (231, 231, 231, 255) if variables.THEME == "Light" else (47, 47, 47, 255)
    tools_icon = tools_icon[:, :, :3]

    def LoadToolbarIcon(name="", size=(25, 25)):
        if os.path.exists(f'{variables.PATH}app/assets/{name.lower()}_{variables.THEME}.png'):
            icon = cv2.resize(cv2.imread(f'{variables.PATH}app/assets/{name.lower()}_{variables.THEME.lower()}.png', cv2.IMREAD_UNCHANGED), size)
            for x in range(icon.shape[1]):
                for y in range(icon.shape[0]):
                    if icon[x][y][3] == 0:
                        icon[x][y] = (231, 231, 231, 255) if variables.THEME == "Light" else (47, 47, 47, 255)
            icon = icon[:, :, :3]
            return icon
    home_icon = LoadToolbarIcon("home")
    ai_icon = LoadToolbarIcon("ai")
    grid_line_icon = LoadToolbarIcon("grid_line")
    grid_dot_icon = LoadToolbarIcon("grid_dot")
    rectangle_icon = LoadToolbarIcon("rectangle")
    circle_icon = LoadToolbarIcon("circle")
    graph_icon = LoadToolbarIcon("graph")
    color_icon = LoadToolbarIcon("color")
    text_icon = LoadToolbarIcon("text")

    def GenerateGridImage(images=[]):
        avg_resolution = 0, 0
        for image in images:
            avg_resolution = (avg_resolution[0] + image.shape[1], avg_resolution[1] + image.shape[0])
        avg_resolution = (avg_resolution[0] / len(images), avg_resolution[1] / len(images))
        temp = []
        for image in images:
            temp.append(cv2.resize(image, (round(avg_resolution[0]), round(avg_resolution[1]))))
        images = temp
        variables.TOOLBAR_ROWS = (len(images) + variables.TOOLBAR_COLUMNS - 1) // variables.TOOLBAR_COLUMNS
        image = numpy.zeros((round(avg_resolution[1]) * variables.TOOLBAR_ROWS + variables.TOOLBAR_PADDING * (variables.TOOLBAR_ROWS - 1), round(avg_resolution[0]) * variables.TOOLBAR_COLUMNS + variables.TOOLBAR_PADDING * (variables.TOOLBAR_COLUMNS - 1), 3), numpy.uint8)
        image[:] = (231, 231, 231) if variables.THEME == "Light" else (47, 47, 47)
        x = 0
        y = 0
        for i, img in enumerate(images):
            image[y:y+img.shape[0], x:x+img.shape[1]] = img
            x += round(avg_resolution[0]) + variables.TOOLBAR_PADDING
            if (i + 1) % variables.TOOLBAR_COLUMNS == 0:
                x = 0
                y += round(avg_resolution[1]) + variables.TOOLBAR_PADDING
        return image
    variables.TOOLBAR = GenerateGridImage((home_icon, ai_icon, grid_line_icon, grid_dot_icon, rectangle_icon, circle_icon, graph_icon, color_icon, text_icon))
    variables.TOOLBAR_HEIGHT = variables.TOOLBAR.shape[0] + 20
    variables.TOOLBAR_WIDTH = variables.TOOLBAR.shape[1] + 20
    #if tabControl.tab(tabControl.select(), "text") == "Draw":
    #    tools.configure(image=tools_icon)
    #    tools.image = tools_icon
    #else:
    #    tools.configure(image=tools_placeholder)
    #    tools.image = tools_placeholder

def Update():
    CurrentTime = time.time()

    if variables.OS == "nt":
        if window.GetWindowStatus(variables.NAME)["Iconic"] == False:
            window.Show(variables.NAME, variables.CACHED_FRAME)
            return

    if window.GetWindowStatus(variables.NAME)["Open"] == None:
        Close()

    WindowX, WindowY = window.GetWindowPosition(variables.NAME)
    WindowWidth, WindowHeight = window.GetWindowSize(variables.NAME)
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

    if variables.PAGE == "Canvas":
        variables.ITEMS.append({
            "Type": "Image",
            "Image": canvas.Frame,
            "X1": 0,
            "Y1": 0,
            "Y2": variables.CANVAS_BOTTOM,
            "X2": variables.CANVAS_RIGHT
        })

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
            "Function": lambda: {setattr(variables, "PAGE", "CUDA"), SetTitleBarHeight(0)},
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

        variables.ITEMS = sorted(variables.ITEMS, key=lambda x: ["Label-First-Render", "Button-First-Render", "Switch-First-Render", "Dropdown-First-Render", "Image-First-Render",
                                                                 "Label", "Button", "Switch", "Dropdown", "Image",
                                                                 "Label-Last-Render", "Button-Last-Render", "Switch-Last-Render", "Dropdown-Last-Render", "Image-Last-Render"].index(x["Type"]))
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

    window.Show(variables.NAME, variables.CACHED_FRAME)