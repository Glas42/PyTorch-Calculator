from src.crashreport import CrashReport
import src.variables as variables
import src.settings as settings

from tkinter import filedialog
import SimpleWindow
import threading
import traceback
import time
import os


RED = "\033[91m"
GREEN = "\033[92m"
GRAY = "\033[90m"
NORMAL = "\033[0m"

SAVING = False
OPENING = False


def MovePathPopup(Title=""):
    try:
        def MovePathPopupThread():
            try:
                while True:
                    HWND = win32gui.FindWindow(None, Title)
                    if HWND != 0:
                        X, Y = SimpleWindow.GetPosition(variables.NAME)
                        WIDTH, HEIGHT = SimpleWindow.GetSize(variables.NAME)
                        win32gui.MoveWindow(HWND, X, Y, WIDTH, HEIGHT, True)
                        win32gui.SetWindowPos(HWND, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                        win32gui.SetWindowLong(HWND, win32con.GWL_EXSTYLE, win32gui.GetWindowLong(HWND, win32con.GWL_EXSTYLE))
                        break
                RECT = win32gui.GetClientRect(HWND)
                TopLeft = win32gui.ClientToScreen(HWND, (RECT[0], RECT[1]))
                BottomRight = win32gui.ClientToScreen(HWND, (RECT[2], RECT[3]))
                XOffset = X - TopLeft[0]
                YOffset = Y - TopLeft[1] + 32
                WidthOffset = WIDTH - (BottomRight[0] - TopLeft[0])
                HeightOffset = HEIGHT - (BottomRight[1] - TopLeft[1]) - 32
                while True:
                    Start = time.time()
                    X, Y = SimpleWindow.GetPosition(variables.NAME)
                    WIDTH, HEIGHT = SimpleWindow.SimpleWindow.GetSize(variables.NAME)
                    if win32gui.FindWindow(None, Title) == 0:
                        break
                    RECT = win32gui.GetClientRect(HWND)
                    TopLeft = win32gui.ClientToScreen(HWND, (RECT[0], RECT[1]))
                    BottomRight = win32gui.ClientToScreen(HWND, (RECT[2], RECT[3]))
                    if X != TopLeft[0] or Y != TopLeft[1] or WIDTH != BottomRight[0] - TopLeft[0] or HEIGHT != BottomRight[1] - TopLeft[1]:
                        win32gui.MoveWindow(HWND, X + XOffset, Y + YOffset, WIDTH + WidthOffset, HEIGHT + HeightOffset, True)
                    TimeToSleep = 1/variables.FPS - (time.time() - Start)
                    if TimeToSleep > 0:
                        time.sleep(TimeToSleep)
            except:
                CrashReport("File - Error in function MovePathPopupThread.", str(traceback.format_exc()))
        if variables.OS != "nt":
            return
        import win32gui, win32con
        threading.Thread(target=MovePathPopupThread, daemon=True).start()
    except:
        CrashReport("File - Error in function MovePathPopup.", str(traceback.format_exc()))


def New():
    try:
        def NewThread():
            try:
                Save(Path=f"{variables.PATH}cache/LastSession.txt")
                while SAVING or OPENING:
                    time.sleep(0.1)
                print(GREEN + "Creating new file..." + NORMAL)
                variables.POPUP = ["Creating new file...", -1, 0.5]
                variables.CANVAS_POSITION = variables.WIDTH // 2, variables.HEIGHT // 2
                variables.CANVAS_ZOOM = 1
                variables.CANVAS_SHOW_GRID = True
                variables.CANVAS_LINE_GRID = False
                variables.DRAW_COLOR = (255, 255, 255) if variables.THEME == "Dark" else (0, 0, 0)
                variables.SMOOTH_LINES = settings.Get("Draw", "SmoothLines", False)
                variables.UPSCALE_LINES = settings.Get("Draw", "UpscaleLines", True)
                variables.ANTI_ALIASING_LINES = settings.Get("Draw", "AntiAliasingLines", True)
                variables.SMOOTH_INTERPOLATION = settings.Get("Draw", "SmoothInterpolation", False)
                variables.MOUSE_SLOWDOWN = settings.Get("Draw", "MouseSlowdown", 1)
                variables.CANVAS_CONTENT = []
                variables.CANVAS_TEMP = []
                variables.CANVAS_DELETE_LIST = []
                variables.DROPDOWNS = {}
                variables.SWITCHES = {}
                print(GRAY + f"-> Show Grid: {variables.CANVAS_SHOW_GRID}" + NORMAL)
                print(GRAY + f"-> Line Grid: {variables.CANVAS_LINE_GRID}" + NORMAL)
                print(GRAY + f"-> Color: {variables.DRAW_COLOR}" + NORMAL)
                print(GRAY + f"-> Smooth Lines: {variables.SMOOTH_LINES}" + NORMAL)
                print(GRAY + f"-> Upscale Lines: {variables.UPSCALE_LINES}" + NORMAL)
                print(GRAY + f"-> Anti-Aliasing Lines: {variables.ANTI_ALIASING_LINES}" + NORMAL)
                print(GRAY + f"-> Smooth Interpolation: {variables.SMOOTH_INTERPOLATION}" + NORMAL)
                print(GREEN + "Created new file successfully!\n" + NORMAL)
                variables.POPUP = ["Created new file successfully!", 0, 0.5]
                variables.PAGE = "Canvas"
            except:
                CrashReport("File - Error in function NewThread.", str(traceback.format_exc()))
                variables.POPUP = ["Error creating new file.", 0, 0.5]
        threading.Thread(target=NewThread, daemon=True).start()
    except:
        CrashReport("File - Error in function New.", str(traceback.format_exc()))


def Save(Path=""):
    try:
        def SaveThread():
            try:
                print(GREEN + "Saving file..." + NORMAL)
                variables.POPUP = ["Saving file...", -1, 0.5]
                if Path == "":
                    MovePathPopup(Title="Select a path to save to")
                    variables.FILE_PATH = filedialog.asksaveasfilename(initialdir=settings.Get("File", "LastDirectory", os.path.dirname(os.path.dirname(variables.PATH))), title="Select a path to save to", filetypes=((".txt","*.txt"), ("all files","*.*")))
                else:
                    variables.FILE_PATH = Path
                if variables.FILE_PATH == "":
                    print(RED + "File not saved!\n" + NORMAL)
                    variables.POPUP = ["File not saved!", 0, 0.5]
                    return
                if variables.FILE_PATH.endswith(".txt") == False:
                    variables.FILE_PATH += ".txt"
                if os.path.exists(os.path.dirname(variables.FILE_PATH)) == False:
                    os.makedirs(os.path.dirname(variables.FILE_PATH))
                if f"{variables.PATH}cache" not in variables.FILE_PATH:
                    settings.Set("File", "LastDirectory", os.path.dirname(variables.FILE_PATH))
                print(GRAY + f"-> {variables.FILE_PATH}" + NORMAL)
                with open(variables.FILE_PATH, "w") as F:
                    F.write(f"""
                        CANVAS_POSITION#{variables.CANVAS_POSITION}###
                        CANVAS_ZOOM#{variables.CANVAS_ZOOM}###
                        CANVAS_SHOW_GRID#{variables.CANVAS_SHOW_GRID}###
                        CANVAS_LINE_GRID#{variables.CANVAS_LINE_GRID}###
                        DRAW_COLOR#{variables.DRAW_COLOR}###
                        SMOOTH_LINES#{variables.SMOOTH_LINES}###
                        UPSCALE_LINES#{variables.UPSCALE_LINES}###
                        ANTI_ALIASING_LINES#{variables.ANTI_ALIASING_LINES}###
                        SMOOTH_INTERPOLATION#{variables.SMOOTH_INTERPOLATION}###
                        MOUSE_SLOWDOWN#{variables.MOUSE_SLOWDOWN}###
                        CANVAS_CONTENT#{variables.CANVAS_CONTENT}###
                        CANVAS_TEMP#{variables.CANVAS_TEMP}###
                        CANVAS_DELETE_LIST#{variables.CANVAS_DELETE_LIST}
                    """.replace(" ", "").replace("\n", ""))
                print(GREEN + "File saved successfully!\n" + NORMAL)
                if f"{variables.PATH}cache" not in variables.FILE_PATH:
                    variables.POPUP = ["File saved successfully!", 0, 0.5]
                else:
                    variables.POPUP = POPUP = [None, 0, 0.5]
                variables.PAGE = "Canvas"
            except:
                CrashReport("File - Error in function SaveThread.", str(traceback.format_exc()))
                variables.POPUP = ["File not saved!", 0, 0.5]
            global SAVING
            SAVING = False
        global SAVING
        SAVING = True
        threading.Thread(target=SaveThread, daemon=True).start()
    except:
        CrashReport("File - Error in function Save.", str(traceback.format_exc()))


def Open(Path=""):
    try:
        def OpenThread():
            try:
                print(GREEN + "Opening file..." + NORMAL)
                variables.POPUP = ["Opening file...", -1, 0.5]
                if Path == "" or os.path.exists(Path) == False:
                    MovePathPopup(Title="Select a text file to open")
                    variables.FILE_PATH = filedialog.askopenfilename(initialdir=settings.Get("File", "LastDirectory", os.path.dirname(os.path.dirname(variables.PATH))), title="Select a text file to open", filetypes=((".txt","*.txt"), ("all files","*.*")))
                else:
                    variables.FILE_PATH = Path
                if variables.FILE_PATH == "" or os.path.exists(variables.FILE_PATH) == False:
                    print(RED + "File not opened!\n" + NORMAL)
                    variables.POPUP = ["File not opened!", 0, 0.5]
                    return
                if f"{variables.PATH}cache" not in variables.FILE_PATH:
                    settings.Set("File", "LastDirectory", os.path.dirname(variables.FILE_PATH))
                print(GRAY + f"-> {variables.FILE_PATH}" + NORMAL)
                with open(variables.FILE_PATH, "r") as F:
                    Content = str(F.read()).replace("\n", "").replace(" ", "")
                    for Item in Content.split("###"):
                        Key, Value = Item.split("#")
                        setattr(variables, Key, eval(Value))
                variables.DROPDOWNS = {}
                variables.SWITCHES = {}
                print(GREEN + "File opened successfully!\n" + NORMAL)
                if f"{variables.PATH}cache" not in variables.FILE_PATH:
                    variables.POPUP = ["File opened successfully!", 0, 0.5]
                else:
                    variables.POPUP = POPUP = [None, 0, 0.5]
                variables.PAGE = "Canvas"
            except:
                CrashReport("File - Error in function OpenThread.", str(traceback.format_exc()))
                variables.POPUP = ["File not opened!", 0, 0.5]
            global OPENING
            OPENING = False
        global OPENING
        OPENING = True
        threading.Thread(target=OpenThread, daemon=True).start()
    except:
        CrashReport("File - Error in function Open.", str(traceback.format_exc()))