import src.variables as variables
import src.settings as settings
import src.console as console
import src.ui as ui

import traceback
import threading
import requests
import pynput
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
        time_to_sleep = 1/variables.FPS - (time.time() - start)
        if time_to_sleep > 0:
            time.sleep(time_to_sleep)
threading.Thread(target=WindowMover, daemon=True).start()

def DrawHandler():
    import ctypes
    import mouse
    smooth_lines = settings.Get("Draw", "SmoothLines", False)
    upscale_lines = settings.Get("Draw", "UpscaleLines", False)
    last_left_clicked = False
    last_right_clicked = False
    last_mouse_x = 0
    last_mouse_y = 0
    move_start = 0, 0
    while variables.BREAK == False:
        try:
            window_x, window_y, window_width, window_height = ui.cv2.getWindowImageRect(variables.WINDOWNAME)
        except:
            variables.BREAK = True
        mouse_x, mouse_y = mouse.get_position()

        left_clicked = ctypes.windll.user32.GetKeyState(0x01) & 0x8000 != 0 and window_x <= mouse_x <= window_x + window_width and window_y <= mouse_y <= window_y + window_height
        right_clicked = ctypes.windll.user32.GetKeyState(0x02) & 0x8000 != 0 and window_x <= mouse_x <= window_x + window_width and window_y <= mouse_y <= window_y + window_height

        with pynput.mouse.Events() as events:
            event = events.get()
            if isinstance(event, pynput.mouse.Events.Scroll):
                canvas_x = (mouse_x - window_x - variables.CANVAS_POSITION[0]) / variables.CANVAS_ZOOM
                canvas_y = (mouse_y - window_y - variables.CANVAS_POSITION[1]) / variables.CANVAS_ZOOM
                if variables.CANVAS_ZOOM < 10000:
                    variables.CANVAS_ZOOM *= 1.1 if event.dy > 0 else 0.9
                elif event.dy < 0:
                    variables.CANVAS_ZOOM *= 0.9
                variables.CANVAS_POSITION = (mouse_x - window_x - canvas_x * variables.CANVAS_ZOOM, mouse_y - window_y - canvas_y * variables.CANVAS_ZOOM)

        if right_clicked == False:
            move_start = mouse_x - variables.CANVAS_POSITION[0], mouse_y - variables.CANVAS_POSITION[1]
        else:
            variables.CANVAS_POSITION = (mouse_x - move_start[0]), (mouse_y - move_start[1])

        if left_clicked == True and (mouse_x - window_x, mouse_y - window_y) not in variables.CANVAS_TEMP:
            variables.CANVAS_TEMP.append(((mouse_x - window_x - variables.CANVAS_POSITION[0]) * 1/variables.CANVAS_ZOOM, (mouse_y - window_y - variables.CANVAS_POSITION[1]) * 1/variables.CANVAS_ZOOM))

        if left_clicked == False and last_left_clicked == True:
            if upscale_lines:
                temp = []
                for _ in range(15):
                    for i in range(len(variables.CANVAS_TEMP)-2):
                        x1, y1 = variables.CANVAS_TEMP[i]
                        x2, y2 = variables.CANVAS_TEMP[i+1]
                        x3, y3 = variables.CANVAS_TEMP[i+2]
                        x = (x1*0.3 + x2*0.4 + x3*0.3)
                        y = (y1*0.3 + y2*0.4 + y3*0.3)
                        temp.append((x, y))
                temp.append(variables.CANVAS_TEMP[-1])
                variables.CANVAS_TEMP = temp

            if smooth_lines:
                temp = []
                for point in variables.CANVAS_TEMP:
                    if point not in temp:
                        temp.append(point)
                variables.CANVAS_TEMP = temp
                smoothness = len(variables.CANVAS_TEMP) // 50
                for _ in range(smoothness):
                    temp = []
                    for i in range(len(variables.CANVAS_TEMP)):
                        if i < smoothness:
                            x_avg = sum(p[0] for p in variables.CANVAS_TEMP[:i+smoothness+1]) // (i+smoothness+1)
                            y_avg = sum(p[1] for p in variables.CANVAS_TEMP[:i+smoothness+1]) // (i+smoothness+1)
                            temp.append((x_avg, y_avg))
                        elif i >= len(variables.CANVAS_TEMP) - smoothness:
                            x_avg = sum(p[0] for p in variables.CANVAS_TEMP[i-smoothness:]) // (len(variables.CANVAS_TEMP) - i + smoothness)
                            y_avg = sum(p[1] for p in variables.CANVAS_TEMP[i-smoothness:]) // (len(variables.CANVAS_TEMP) - i + smoothness)
                            temp.append((x_avg, y_avg))
                        else:
                            x_avg = sum(p[0] for p in variables.CANVAS_TEMP[i-smoothness:i+smoothness+1]) // (2*smoothness + 1)
                            y_avg = sum(p[1] for p in variables.CANVAS_TEMP[i-smoothness:i+smoothness+1]) // (2*smoothness + 1)
                            temp.append((x_avg, y_avg))
                    variables.CANVAS_TEMP = temp

            temp = []
            for point in variables.CANVAS_TEMP:
                if point not in temp:
                    temp.append(point)
            variables.FILE_CONTENT.append(temp)
            variables.CANVAS_TEMP = []

        last_mouse_x, last_mouse_y = mouse_x, mouse_y
        last_left_clicked, last_right_clicked = left_clicked, right_clicked
threading.Thread(target=DrawHandler, daemon=True).start()

def KeyHandler():
    import ctypes
    last_left_clicked, last_right_clicked = False, False
    last_ctrl_z_clicked, last_ctrl_y_clicked = False, False
    last_ctrl_c_clicked, last_ctrl_v_clicked, last_ctrl_x_clicked = False, False, False
    while variables.BREAK == False:
        start = time.time()

        window_is_foreground = win32gui.GetWindowText(win32gui.GetForegroundWindow()) == variables.WINDOWNAME
        ctrl_z_clicked = ctypes.windll.user32.GetKeyState(0x5A) & 0x8000 != 0 and window_is_foreground
        ctrl_y_clicked = ctypes.windll.user32.GetKeyState(0x59) & 0x8000 != 0 and window_is_foreground
        ctrl_c_clicked = ctypes.windll.user32.GetKeyState(0x43) & 0x8000 != 0 and window_is_foreground
        ctrl_v_clicked = ctypes.windll.user32.GetKeyState(0x56) & 0x8000 != 0 and window_is_foreground
        ctrl_x_clicked = ctypes.windll.user32.GetKeyState(0x58) & 0x8000 != 0 and window_is_foreground

        if ctrl_z_clicked == True and last_ctrl_z_clicked == False:
            if len(variables.FILE_CONTENT) > 0:
                variables.CANVAS_DELETE_LIST.append(variables.FILE_CONTENT[-1])
                variables.FILE_CONTENT.pop()

        if ctrl_y_clicked == True and last_ctrl_y_clicked == False:
            if len(variables.CANVAS_DELETE_LIST) > 0:
                variables.FILE_CONTENT.append(variables.CANVAS_DELETE_LIST[-1])
                variables.CANVAS_DELETE_LIST.pop()

        last_ctrl_z_clicked, last_ctrl_y_clicked = ctrl_z_clicked, ctrl_y_clicked
        last_ctrl_c_clicked, last_ctrl_v_clicked, last_ctrl_x_clicked = ctrl_c_clicked, ctrl_v_clicked, ctrl_x_clicked

        time_to_sleep = 1/variables.FPS - (time.time() - start)
        if time_to_sleep > 0:
            time.sleep(time_to_sleep)
threading.Thread(target=KeyHandler, daemon=True).start()

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
        for x, y in variables.CANVAS_TEMP:
            if last_point != None:
                point_x1 = round((last_point[0] + variables.CANVAS_POSITION[0] * 1/variables.CANVAS_ZOOM) * variables.CANVAS_ZOOM)
                point_y1 = round((last_point[1] + variables.CANVAS_POSITION[1] * 1/variables.CANVAS_ZOOM) * variables.CANVAS_ZOOM)
                point_x2 = round((x + variables.CANVAS_POSITION[0] * 1/variables.CANVAS_ZOOM) * variables.CANVAS_ZOOM)
                point_y2 = round((y + variables.CANVAS_POSITION[1] * 1/variables.CANVAS_ZOOM) * variables.CANVAS_ZOOM)
                if 0 <= point_x1 < frame.shape[1] or 0 <= point_y1 < frame.shape[0] or 0 <= point_x2 < frame.shape[1] or 0 <= point_y2 < frame.shape[0]:
                    ui.cv2.line(frame, (point_x1, point_y1), (point_x2, point_y2), variables.CANVAS_DRAW_COLOR, 3)
            last_point = (x, y)

        if len(variables.CANVAS_TEMP) == 1:
            point_x = round((variables.CANVAS_TEMP[0][0] + variables.CANVAS_POSITION[0] * 1/variables.CANVAS_ZOOM) * variables.CANVAS_ZOOM)
            point_y = round((variables.CANVAS_TEMP[0][1] + variables.CANVAS_POSITION[1] * 1/variables.CANVAS_ZOOM) * variables.CANVAS_ZOOM)
            if 0 <= point_x < frame.shape[1] or 0 <= point_y < frame.shape[0]:
                ui.cv2.circle(frame, (point_x, point_y), 3, variables.CANVAS_DRAW_COLOR, -1)
        for i in variables.FILE_CONTENT:
            last_point = None
            for x, y in i:
                if last_point != None:
                    point_x1 = round((last_point[0] + variables.CANVAS_POSITION[0] * 1/variables.CANVAS_ZOOM) * variables.CANVAS_ZOOM)
                    point_y1 = round((last_point[1] + variables.CANVAS_POSITION[1] * 1/variables.CANVAS_ZOOM) * variables.CANVAS_ZOOM)
                    point_x2 = round((x + variables.CANVAS_POSITION[0] * 1/variables.CANVAS_ZOOM) * variables.CANVAS_ZOOM)
                    point_y2 = round((y + variables.CANVAS_POSITION[1] * 1/variables.CANVAS_ZOOM) * variables.CANVAS_ZOOM)
                    if 0 <= point_x1 < frame.shape[1] or 0 <= point_y1 < frame.shape[0] or 0 <= point_x2 < frame.shape[1] or 0 <= point_y2 < frame.shape[0]:
                        ui.cv2.line(frame, (point_x1, point_y1), (point_x2, point_y2), variables.CANVAS_DRAW_COLOR, 3)
                last_point = (x, y)
            if len(i) == 1:
                point_x = round((i[0][0] + variables.CANVAS_POSITION[0] * 1/variables.CANVAS_ZOOM) * variables.CANVAS_ZOOM)
                point_y = round((i[0][1] + variables.CANVAS_POSITION[1] * 1/variables.CANVAS_ZOOM) * variables.CANVAS_ZOOM)
                if 0 <= point_x < frame.shape[1] or 0 <= point_y < frame.shape[0]:
                    ui.cv2.circle(frame, (point_x, point_y), 3, variables.CANVAS_DRAW_COLOR, -1)

        ui.cv2.imshow(variables.WINDOWNAME, frame)
        ui.cv2.waitKey(1)

    variables.ROOT.update()

    time_to_sleep = 1/variables.FPS - (time.time() - start)
    if time_to_sleep > 0:
        time.sleep(time_to_sleep)

if settings.Get("Console", "HideConsole", False):
    console.RestoreConsole()
    console.CloseConsole()