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


def MovePathPopup(Title=""):
    try:
        if variables.OS != "nt":
            return
        import win32gui, win32con
        def MovePathPopupThread():
            try:
                while True:
                    HWND = win32gui.FindWindow(None, Title)
                    if HWND != 0:
                        X, Y = SimpleWindow.GetWindowPosition(variables.NAME)
                        WIDTH, HEIGHT = SimpleWindow.GetWindowSize(variables.NAME)
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
                    X, Y = SimpleWindow.GetWindowPosition(variables.NAME)
                    WIDTH, HEIGHT = SimpleWindow.GetWindowSize(variables.NAME)
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
        threading.Thread(target=MovePathPopupThread).start()
    except:
        CrashReport("File - Error in function MovePathPopup.", str(traceback.format_exc()))


def New():
    try:
        Save(Path=f"{variables.PATH}cache/LastSession.txt")
        print(GREEN + "Creating new file!" + NORMAL)
        variables.POPUP = ["Creating new file!", 0, 0.5]
        variables.CANVAS_POSITION = variables.WIDTH // 2, variables.HEIGHT // 2
        variables.CANVAS_ZOOM = 1
        variables.CANVAS_SHOW_GRID = True
        variables.CANVAS_GRID_TYPE = "DOT"
        variables.CANVAS_CONTENT = []
        variables.CANVAS_TEMP = []
        variables.CANVAS_DELETE_LIST = []
        variables.DRAW_COLOR = (0, 0, 0) if variables.THEME == "light" else (255, 255, 255)
        variables.PAGE = "Canvas"
        print(GRAY + f"-> Show Grid: {variables.CANVAS_SHOW_GRID}" + NORMAL)
        print(GRAY + f"-> Grid Type: {variables.CANVAS_GRID_TYPE}" + NORMAL)
        print(GRAY + f"-> Color: {variables.DRAW_COLOR}" + NORMAL)
        print()
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
                with open(variables.FILE_PATH, "w") as f:
                    f.write(f"""
                        {variables.CANVAS_POSITION}#
                        {variables.CANVAS_ZOOM}#
                        {variables.CANVAS_SHOW_GRID}#
                        {variables.CANVAS_GRID_TYPE}#
                        {variables.CANVAS_CONTENT}#
                        {variables.CANVAS_TEMP}#
                        {variables.CANVAS_DELETE_LIST}#
                        {variables.DRAW_COLOR}
                    """.replace(" ", "").replace("\n", ""))
                print(GREEN + "File saved successfully!\n" + NORMAL)
                variables.POPUP = ["File saved successfully!", 0, 0.5]
                variables.PAGE = "Canvas"
            except:
                CrashReport("File - Error in function SaveThread.", str(traceback.format_exc()))
        threading.Thread(target=SaveThread).start()
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
                with open(variables.FILE_PATH, "r") as f:
                    content = str(f.read()).split("#")
                    variables.CANVAS_POSITION = eval(content[0])
                    variables.CANVAS_ZOOM = float(content[1])
                    variables.CANVAS_SHOW_GRID = bool(content[2])
                    variables.CANVAS_GRID_TYPE = str(content[3])
                    variables.CANVAS_CONTENT = eval(content[4])
                    variables.CANVAS_TEMP = eval(content[5])
                    variables.CANVAS_DELETE_LIST = eval(content[6])
                    variables.DRAW_COLOR = eval(content[7])
                print(GREEN + "File opened successfully!\n" + NORMAL)
                variables.POPUP = ["File opened successfully!", 0, 0.5]
                variables.PAGE = "Canvas"
            except:
                CrashReport("File - Error in function OpenThread.", str(traceback.format_exc()))
        threading.Thread(target=OpenThread).start()
    except:
        CrashReport("File - Error in function Open.", str(traceback.format_exc()))