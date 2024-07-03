import src.variables as variables
import src.settings as settings
import src.console as console
import src.ui as ui

import traceback
import threading
import requests
import numpy
import time
import os

if settings.Get("Console", "HideConsole", False):
    console.HideConsole()
if variables.OS == "nt":
    import win32gui, win32con

def update_check():
    try:
        remote_version = requests.get("https://raw.githubusercontent.com/Glas42/PyTorch-Calculator/main/version.txt").text.strip()
        changelog = requests.get("https://raw.githubusercontent.com/Glas42/PyTorch-Calculator/main/changelog.txt").text.strip()
    except:
        print(f"{variables.RED}Failed to check for updates:{variables.NORMAL}\n" + str(traceback.format_exc()))
    if remote_version != variables.VERSION and settings.Get("Update", "AutoUpdate", True):
        try:
            print(f"New version available: {remote_version}\nChangelog:\n{changelog}")
            os.chdir(variables.PATH)
            os.system("git stash")
            os.system("git pull")
        except:
            print(f"{variables.RED}Failed to update: {variables.NORMAL}\n" + str(traceback.format_exc()))
    else:
        print("No update available, current version: " + variables.VERSION)

ui.initialize()
ui.createUI()

frame = ui.background.copy()
current_tab = None
last_tab = None
position = 0, 0
points = []

def WindowMover():
    last_window_position = None, None, None, None
    while variables.BREAK == False:
        start = time.time()
        try:
            if current_tab == "Draw":
                rect = win32gui.GetClientRect(variables.TK_HWND)
                tl = win32gui.ClientToScreen(variables.TK_HWND, (rect[0], rect[1]))
                br = win32gui.ClientToScreen(variables.TK_HWND, (rect[2], rect[3]))
                window_position = (tl[0], tl[1], br[0] - tl[0], br[1] - tl[1])
                if window_position != last_window_position:
                    win32gui.MoveWindow(variables.HWND, window_position[0] + 5, window_position[1] + 45, window_position[2] - 10, window_position[3] - 50, True)
                    ui.background = numpy.zeros((window_position[3] - 50, window_position[2] - 10, 3), numpy.uint8)
                    ui.background[:] = ((250, 250, 250) if settings.Get("UI", "theme") == "light" else (28, 28, 28))
                    if ui.cv2.getWindowProperty(variables.WINDOWNAME, ui.cv2.WND_PROP_TOPMOST) != 1:
                        ui.cv2.setWindowProperty(variables.WINDOWNAME, ui.cv2.WND_PROP_TOPMOST, 1)
                last_window_position = window_position
        except:
            pass
        time_to_sleep = 1/60 - (time.time() - start)
        if time_to_sleep > 0:
            time.sleep(time_to_sleep)
threading.Thread(target=WindowMover, daemon=True).start()

def DrawHandler():
    import ctypes
    import mouse
    global points
    global position
    smooth_lines = settings.Get("Draw", "SmoothLines", False)
    last_left_clicked = False
    last_right_clicked = False
    last_mouse_x = None
    last_mouse_y = None
    move_start = 0, 0
    while variables.BREAK == False:
        try:
            window_x, window_y, window_width, window_height = ui.cv2.getWindowImageRect(variables.WINDOWNAME)
        except:
            variables.BREAK = True
        mouse_x, mouse_y = mouse.get_position()
        if last_mouse_x is None: last_mouse_x = mouse_x
        if last_mouse_y is None: last_mouse_y = mouse_y

        left_clicked = True if ctypes.windll.user32.GetKeyState(0x01) & 0x8000 != 0 and window_x <= mouse_x <= window_x + window_width and window_y <= mouse_y <= window_y + window_height else False
        right_clicked = True if ctypes.windll.user32.GetKeyState(0x02) & 0x8000 != 0 and window_x <= mouse_x <= window_x + window_width and window_y <= mouse_y <= window_y + window_height else False

        if right_clicked == False:
            move_start = mouse_x - position[0], mouse_y - position[1]
        else:
            position = (mouse_x - move_start[0], mouse_y - move_start[1])

        if left_clicked == True and (mouse_x - window_x, mouse_y - window_y) not in points:
            points.append((mouse_x - window_x - position[0], mouse_y - window_y - position[1]))

        if left_clicked == False and last_left_clicked == True:
            if smooth_lines:
                temp = []
                for point in points:
                    if point not in temp:
                        temp.append(point)
                points = temp
                smoothness = len(points) // 50
                for _ in range(smoothness):
                    temp = []
                    for i in range(len(points)):
                        if i < smoothness:
                            x_avg = sum(p[0] for p in points[:i+smoothness+1]) // (i+smoothness+1)
                            y_avg = sum(p[1] for p in points[:i+smoothness+1]) // (i+smoothness+1)
                            temp.append((x_avg, y_avg))
                        elif i >= len(points) - smoothness:
                            x_avg = sum(p[0] for p in points[i-smoothness:]) // (len(points) - i + smoothness)
                            y_avg = sum(p[1] for p in points[i-smoothness:]) // (len(points) - i + smoothness)
                            temp.append((x_avg, y_avg))
                        else:
                            x_avg = sum(p[0] for p in points[i-smoothness:i+smoothness+1]) // (2*smoothness + 1)
                            y_avg = sum(p[1] for p in points[i-smoothness:i+smoothness+1]) // (2*smoothness + 1)
                            temp.append((x_avg, y_avg))
                    points = temp

            temp = []
            for point in points:
                if point not in temp:
                    temp.append(point)
            points = temp
            variables.FILE_CONTENT.append(points)
            points = []

        last_mouse_x, last_mouse_y = mouse_x, mouse_y
        last_left_clicked, last_right_clicked = left_clicked, right_clicked
threading.Thread(target=DrawHandler, daemon=True).start()

while variables.BREAK == False:
    start = time.time()

    current_tab = ui.tabControl.tab(ui.tabControl.select(), "text")
    if current_tab == "Draw" and str(win32gui.GetWindowText(win32gui.GetForegroundWindow())) == variables.WINDOWNAME:
        if win32gui.GetWindowPlacement(variables.HWND)[1] != 1:
            win32gui.ShowWindow(variables.HWND, 1)
    elif win32gui.GetWindowPlacement(variables.HWND)[1] == 1:
        win32gui.ShowWindow(variables.HWND, 2)
    last_tab = current_tab

    if current_tab == "Draw":
        frame = ui.background.copy()
        last_point = None
        for x, y in points:
            if last_point != None:
                ui.cv2.line(frame, (last_point[0] + position[0], last_point[1] + position[1]), (x + position[0], y + position[1]), (255, 255, 255), 3)
            last_point = (x, y)
        if len(points) == 1:
            ui.cv2.circle(frame, (points[0][0] + position[0], points[0][1] + position[1]), 3, (255, 255, 255), -1)
        for i in variables.FILE_CONTENT:
            last_point = None
            for x, y in i:
                if last_point != None:
                    ui.cv2.line(frame, (last_point[0] + position[0], last_point[1] + position[1]), (x + position[0], y + position[1]), (255, 255, 255), 3)
                last_point = (x, y)
            if len(i) == 1:
                ui.cv2.circle(frame, (i[0][0] + position[0], i[0][1] + position[1]), 3, (255, 255, 255), -1)
        ui.cv2.imshow(variables.WINDOWNAME, frame)
        ui.cv2.waitKey(1)

    variables.ROOT.update()

    time_to_sleep = 1/60 - (time.time() - start)
    if time_to_sleep > 0:
        time.sleep(time_to_sleep)

if settings.Get("Console", "HideConsole", False):
    console.RestoreConsole()
    console.CloseConsole()