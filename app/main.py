import src.variables as variables
import src.settings as settings
import src.console as console
import src.ui as ui

import traceback
import threading
import requests
import pynput
import time
import sys
import cv2
import os

if settings.Get("Console", "HideConsole", False):
    console.HideConsole()

if variables.OS == "nt":
    import win32gui
    import ctypes

settings.Get("Draw", "SmoothLines", False)
settings.Get("Draw", "UpscaleLines", True)
settings.Get("Draw", "MouseSlowdown", 1)

def update_check():
    try:
        remote_version = requests.get("https://raw.githubusercontent.com/Glas42/PyTorch-Calculator/main/version.txt").text.strip()
    except:
        print(f"{variables.RED}Failed to check for updates:{variables.NORMAL}\n" + str(traceback.format_exc()))
    if remote_version != variables.VERSION and settings.Get("Update", "AutoUpdate", True):
        try:
            print(f"New version available: {remote_version}")
            os.chdir(variables.PATH)
            os.system("git stash")
            os.system("git pull")
        except:
            print(f"{variables.RED}Failed to update: {variables.NORMAL}\n" + str(traceback.format_exc()))
    else:
        print("No update available, current version: " + variables.VERSION)
update_check() if settings.Get("Update", "AutoUpdate", True) else print("Update check disabled, current version: " + variables.VERSION)

def GetMouseSpeed():
    speed = ctypes.c_int()
    ctypes.windll.user32.SystemParametersInfoA(112, 0, ctypes.byref(speed), 0)
    return speed.value

def SetMouseSpeed(speed):
    speed = int(speed)
    if speed < 1:
        speed = 1
    elif speed > 20:
        speed = 20
    ctypes.windll.user32.SystemParametersInfoA(113, 0, speed, 0)

variables.DEFAULT_MOUSE_SPEED = GetMouseSpeed()

ui.Initialize()
ui.CreateUI()
ui.LoadToolBar()

if len(sys.argv) > 1:
    variables.FILE_PATH = sys.argv[1]
    settings.Set("Load", "LastDirectory", os.path.dirname(variables.FILE_PATH))
    if not variables.FILE_PATH.endswith(".txt"):
        variables.FILE_PATH += ".txt"
    with open(variables.FILE_PATH, "r") as f:
        content = str(f.read()).split("#")
        variables.CANVAS_POSITION = eval(content[0])
        variables.CANVAS_ZOOM = float(content[1])
        variables.CANVAS_SHOW_GRID = bool(content[2])
        variables.CANVAS_GRID_TYPE = str(content[3])
        variables.CANVAS_CONTENT = eval(content[4])
        variables.CANVAS_TEMP = eval(content[5])
        variables.CANVAS_DELETE_LIST = eval(content[6])
        variables.CANVAS_DRAW_COLOR = eval(content[7])

AntiAliasingLines = settings.Get("Draw", "AntiAliasingLines", False)
frame = ui.background.copy()
last_frame = None
last_content = None
current_tab = None
last_tab = None

def DrawHandler():
    import ctypes
    import mouse
    smooth_lines = settings.Get("Draw", "SmoothLines", False)
    upscale_lines = settings.Get("Draw", "UpscaleLines", True)
    smooth_interpolation = settings.Get("Draw", "SmoothInterpolation", False)
    last_left_clicked = False
    last_right_clicked = False
    last_mouse_x = 0
    last_mouse_y = 0
    move_start = 0, 0
    while variables.BREAK == False:
        if win32gui.GetForegroundWindow() != variables.HWND or current_tab != "Draw":
            time.sleep(0.1)
            continue

        rect = win32gui.GetClientRect(variables.HWND)
        tl = win32gui.ClientToScreen(variables.HWND, (rect[0], rect[1]))
        br = win32gui.ClientToScreen(variables.HWND, (rect[2], rect[3]))
        window_x, window_y, window_width, window_height = tl[0], tl[1] + 40, br[0] - tl[0], br[1] - tl[1]
        mouse_x, mouse_y = mouse.get_position()

        left_clicked = ctypes.windll.user32.GetKeyState(0x01) & 0x8000 != 0 and window_x <= mouse_x <= window_x + window_width and window_y <= mouse_y <= window_y + window_height
        right_clicked = ctypes.windll.user32.GetKeyState(0x02) & 0x8000 != 0 and window_x <= mouse_x <= window_x + window_width and window_y <= mouse_y <= window_y + window_height

        if window_x <= mouse_x <= window_x + window_width and window_y <= mouse_y <= window_y + window_height:
            if GetMouseSpeed() == variables.DEFAULT_MOUSE_SPEED:
                SetMouseSpeed(variables.DEFAULT_MOUSE_SPEED * settings.Get("Draw", "MouseSlowdown", 1))
        else:
            if GetMouseSpeed() != variables.DEFAULT_MOUSE_SPEED:
                SetMouseSpeed(variables.DEFAULT_MOUSE_SPEED)

        if window_x + window_width - 40 <= mouse_x <= window_x + window_width and window_y - 40 <= mouse_y <= window_y and variables.TOOLBAR_HOVERED == False:
            variables.TOOLBAR_HOVERED = True
        elif window_x + window_width - variables.TOOLBAR_WIDTH - 20 <= mouse_x <= window_x + window_width and window_y - 40 <= mouse_y <= window_y + variables.TOOLBAR_HEIGHT + 20 and variables.TOOLBAR_HOVERED == True:
            variables.TOOLBAR_HOVERED = True
        else:
            variables.TOOLBAR_HOVERED = False

            if window_x <= mouse_x <= window_x + window_width and window_y <= mouse_y <= window_y + window_height:
                with pynput.mouse.Events() as events:
                    event = events.get()
                    if isinstance(event, pynput.mouse.Events.Scroll):
                        canvas_x = (mouse_x - window_x - variables.CANVAS_POSITION[0]) / variables.CANVAS_ZOOM
                        canvas_y = (mouse_y - window_y - variables.CANVAS_POSITION[1]) / variables.CANVAS_ZOOM
                        if variables.CANVAS_ZOOM < 10000:
                            variables.CANVAS_ZOOM = variables.CANVAS_ZOOM * 1.1 if event.dy > 0 else variables.CANVAS_ZOOM / 1.1
                        elif event.dy < 0:
                            variables.CANVAS_ZOOM /= 1.1
                        variables.CANVAS_POSITION = (mouse_x - window_x - canvas_x * variables.CANVAS_ZOOM, mouse_y - window_y - canvas_y * variables.CANVAS_ZOOM)

            if right_clicked == False:
                move_start = mouse_x - variables.CANVAS_POSITION[0], mouse_y - variables.CANVAS_POSITION[1]
            else:
                variables.CANVAS_POSITION = (mouse_x - move_start[0]), (mouse_y - move_start[1])

            if left_clicked == True and (mouse_x - window_x, mouse_y - window_y) not in variables.CANVAS_TEMP:
                variables.CANVAS_TEMP.append(((mouse_x - window_x - variables.CANVAS_POSITION[0]) * 1/variables.CANVAS_ZOOM, (mouse_y - window_y - variables.CANVAS_POSITION[1]) * 1/variables.CANVAS_ZOOM))

            if left_clicked == False and last_left_clicked == True:
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

                if smooth_interpolation:
                    if len(variables.CANVAS_TEMP) > 1:
                        temp = []
                        for i in range(len(variables.CANVAS_TEMP) - 1):
                            p0 = variables.CANVAS_TEMP[max(i - 1, 0)]
                            p1 = variables.CANVAS_TEMP[i]
                            p2 = variables.CANVAS_TEMP[min(i + 1, len(variables.CANVAS_TEMP) - 1)]
                            p3 = variables.CANVAS_TEMP[min(i + 2, len(variables.CANVAS_TEMP) - 1)]
                            for t in ui.numpy.linspace(0, 1, 50):
                                x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t**2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t**3)
                                y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t**2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t**3)
                                temp.append([x, y])
                        variables.CANVAS_TEMP = temp

                temp = []
                temp.append((min(p[0] for p in variables.CANVAS_TEMP), min(p[1] for p in variables.CANVAS_TEMP), max(p[0] for p in variables.CANVAS_TEMP), max(p[1] for p in variables.CANVAS_TEMP)))
                for point in variables.CANVAS_TEMP:
                    if point not in temp:
                        temp.append(point)
                variables.CANVAS_CONTENT.append(temp)
                variables.CANVAS_TEMP = []

        last_mouse_x, last_mouse_y = mouse_x, mouse_y
        last_left_clicked, last_right_clicked = left_clicked, right_clicked
threading.Thread(target=DrawHandler, daemon=True).start()

def KeyHandler():
    import ctypes
    last_left_clicked, last_right_clicked = False, False
    last_ctrl_z_clicked, last_ctrl_y_clicked = False, False
    last_ctrl_s_clicked, last_ctrl_n_clicked = False, False
    last_ctrl_c_clicked, last_ctrl_v_clicked, last_ctrl_x_clicked, last_ctrl_d_clicked = False, False, False, False
    while variables.BREAK == False:
        if win32gui.GetForegroundWindow() != variables.HWND or current_tab != "Draw":
            time.sleep(0.1)
            continue

        start = time.time()

        window_is_foreground = win32gui.GetWindowText(win32gui.GetForegroundWindow()) == variables.WINDOWNAME
        ctrl_z_clicked = ctypes.windll.user32.GetKeyState(0x5A) & 0x8000 != 0 and window_is_foreground
        ctrl_y_clicked = ctypes.windll.user32.GetKeyState(0x59) & 0x8000 != 0 and window_is_foreground
        ctrl_s_clicked = ctypes.windll.user32.GetKeyState(0x53) & 0x8000 != 0 and window_is_foreground
        ctrl_n_clicked = ctypes.windll.user32.GetKeyState(0x4E) & 0x8000 != 0 and window_is_foreground
        ctrl_c_clicked = ctypes.windll.user32.GetKeyState(0x43) & 0x8000 != 0 and window_is_foreground
        ctrl_v_clicked = ctypes.windll.user32.GetKeyState(0x56) & 0x8000 != 0 and window_is_foreground
        ctrl_x_clicked = ctypes.windll.user32.GetKeyState(0x58) & 0x8000 != 0 and window_is_foreground
        ctrl_d_clicked = ctypes.windll.user32.GetKeyState(0x44) & 0x8000 != 0 and window_is_foreground

        if ctrl_z_clicked == True and last_ctrl_z_clicked == False:
            if len(variables.CANVAS_CONTENT) > 0:
                variables.CANVAS_DELETE_LIST.append(variables.CANVAS_CONTENT[-1])
                variables.CANVAS_CONTENT.pop()

        if ctrl_y_clicked == True and last_ctrl_y_clicked == False:
            if len(variables.CANVAS_DELETE_LIST) > 0:
                variables.CANVAS_CONTENT.append(variables.CANVAS_DELETE_LIST[-1])
                variables.CANVAS_DELETE_LIST.pop()

        last_ctrl_z_clicked, last_ctrl_y_clicked = ctrl_z_clicked, ctrl_y_clicked
        last_ctrl_s_clicked, last_ctrl_n_clicked = ctrl_s_clicked, ctrl_n_clicked
        last_ctrl_c_clicked, last_ctrl_v_clicked, last_ctrl_x_clicked, last_ctrl_d_clicked = ctrl_c_clicked, ctrl_v_clicked, ctrl_x_clicked, ctrl_d_clicked

        time_to_sleep = 1/variables.FPS - (time.time() - start)
        if time_to_sleep > 0:
            time.sleep(time_to_sleep)
threading.Thread(target=KeyHandler, daemon=True).start()

while variables.BREAK == False:
    start = time.time()

    current_tab = ui.tabControl.tab(ui.tabControl.select(), "text")

    if current_tab != last_tab:
        if current_tab == "Draw":
            ui.tools.configure(image=ui.tools_icon)
            ui.tools.image = ui.tools_icon
        else:
            ui.tools.configure(image=ui.tools_placeholder)
            ui.tools.image = ui.tools_placeholder
    last_tab = current_tab

    content = (len(variables.CANVAS_CONTENT),
                    variables.CANVAS_POSITION,
                    variables.CANVAS_ZOOM,
                    variables.CANVAS_SHOW_GRID,
                    variables.CANVAS_GRID_TYPE,
                    len(variables.CANVAS_TEMP),
                    len(variables.CANVAS_DELETE_LIST),
                    variables.CANVAS_DRAW_COLOR,
                    variables.TOOLBAR_HOVERED)

    if current_tab == "Draw" and last_content != content:
        if ui.background.shape != (variables.ROOT.winfo_height() - 40, variables.ROOT.winfo_width(), 3):
            ui.background = ui.numpy.zeros((variables.ROOT.winfo_height() - 40, variables.ROOT.winfo_width(), 3), ui.numpy.uint8)
            ui.background[:] = ((250, 250, 250) if variables.THEME == "light" else (28, 28, 28))
        frame = ui.background.copy()
        CANVAS_CONTENT = variables.CANVAS_CONTENT
        CANVAS_POSITION = variables.CANVAS_POSITION
        CANVAS_ZOOM = variables.CANVAS_ZOOM
        if variables.CANVAS_SHOW_GRID == True:
            grid_size = 50
            grid_width = round(frame.shape[1] / (grid_size * CANVAS_ZOOM))
            grid_height = round(frame.shape[0] / (grid_size * CANVAS_ZOOM))
            if CANVAS_ZOOM > 0.05:
                if variables.CANVAS_GRID_TYPE == "LINE":
                    for x in range(0, grid_width):
                        point_x = round((x * grid_size + CANVAS_POSITION[0] / CANVAS_ZOOM % grid_size) * CANVAS_ZOOM)
                        cv2.line(frame, (point_x, 0), (point_x, frame.shape[0]), (127, 127, 127), 1, cv2.LINE_AA if AntiAliasingLines == True else cv2.LINE_8)
                    for y in range(0, grid_height):
                        point_y = round((y * grid_size + CANVAS_POSITION[1] / CANVAS_ZOOM % grid_size) * CANVAS_ZOOM)
                        cv2.line(frame, (0, point_y), (frame.shape[1], point_y), (127, 127, 127), 1, cv2.LINE_AA if AntiAliasingLines == True else cv2.LINE_8)
                else:
                    for x in range(0, grid_width):
                        point_x = round((x * grid_size + CANVAS_POSITION[0] / CANVAS_ZOOM % grid_size) * CANVAS_ZOOM)
                        for y in range(0, grid_height):
                            point_y = round((y * grid_size + CANVAS_POSITION[1] / CANVAS_ZOOM % grid_size) * CANVAS_ZOOM)
                            cv2.circle(frame, (point_x, point_y), 1, (127, 127, 127), -1, cv2.LINE_AA if AntiAliasingLines == True else cv2.LINE_8)

        last_point = None
        for x, y in variables.CANVAS_TEMP:
            if last_point != None:
                point_x1 = round((last_point[0] + CANVAS_POSITION[0] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                point_y1 = round((last_point[1] + CANVAS_POSITION[1] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                point_x2 = round((x + CANVAS_POSITION[0] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                point_y2 = round((y + CANVAS_POSITION[1] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                if 0 <= point_x1 < frame.shape[1] or 0 <= point_y1 < frame.shape[0] or 0 <= point_x2 < frame.shape[1] or 0 <= point_y2 < frame.shape[0]:
                    cv2.line(frame, (point_x1, point_y1), (point_x2, point_y2), variables.CANVAS_DRAW_COLOR, 3, cv2.LINE_AA if AntiAliasingLines == True else cv2.LINE_8)
            last_point = (x, y)

        if len(variables.CANVAS_TEMP) == 1:
            point_x = round((variables.CANVAS_TEMP[0][0] + CANVAS_POSITION[0] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
            point_y = round((variables.CANVAS_TEMP[0][1] + CANVAS_POSITION[1] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
            if 0 <= point_x < frame.shape[1] or 0 <= point_y < frame.shape[0]:
                cv2.circle(frame, (point_x, point_y), 3, variables.CANVAS_DRAW_COLOR, -1, cv2.LINE_AA if AntiAliasingLines == True else cv2.LINE_8)
        for i in CANVAS_CONTENT:
            last_point = None
            min_x, min_y, max_x, max_y = i[0]
            min_x = round((min_x + CANVAS_POSITION[0] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
            min_y = round((min_y + CANVAS_POSITION[1] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
            max_x = round((max_x + CANVAS_POSITION[0] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
            max_y = round((max_y + CANVAS_POSITION[1] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
            if max_x >= 0 and min_x < frame.shape[1] and max_y >= 0 and min_y < frame.shape[0]:
                if len(i[0]) == 4:
                    i = i[1:]
                for x, y in i:
                    if last_point != None:
                        point_x1 = round((last_point[0] + CANVAS_POSITION[0] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                        point_y1 = round((last_point[1] + CANVAS_POSITION[1] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                        point_x2 = round((x + CANVAS_POSITION[0] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                        point_y2 = round((y + CANVAS_POSITION[1] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                        if 0 <= point_x1 < frame.shape[1] or 0 <= point_y1 < frame.shape[0] or 0 <= point_x2 < frame.shape[1] or 0 <= point_y2 < frame.shape[0]:
                            cv2.line(frame, (point_x1, point_y1), (point_x2, point_y2), variables.CANVAS_DRAW_COLOR, 3, cv2.LINE_AA if AntiAliasingLines == True else cv2.LINE_8)
                    last_point = (x, y)
                if len(i) == 1:
                    point_x = round((i[0][0] + CANVAS_POSITION[0] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                    point_y = round((i[0][1] + CANVAS_POSITION[1] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                    if 0 <= point_x < frame.shape[1] or 0 <= point_y < frame.shape[0]:
                        cv2.circle(frame, (point_x, point_y), 3, variables.CANVAS_DRAW_COLOR, -1, cv2.LINE_AA if AntiAliasingLines == True else cv2.LINE_8)

        if variables.TOOLBAR_HOVERED == True:
            cv2.rectangle(frame, (frame.shape[1] - variables.TOOLBAR_WIDTH -1, 20), (frame.shape[1] - 21, variables.TOOLBAR_HEIGHT), (231, 231, 231) if variables.THEME == "light" else (47, 47, 47), 20, cv2.LINE_AA)
            cv2.rectangle(frame, (frame.shape[1] - variables.TOOLBAR_WIDTH - 1, 20), (frame.shape[1] - 21, variables.TOOLBAR_HEIGHT), (231, 231, 231) if variables.THEME == "light" else (47, 47, 47), -1, cv2.LINE_AA)
            frame[20:variables.TOOLBAR_HEIGHT, frame.shape[1] - variables.TOOLBAR_WIDTH -1:frame.shape[1] - 21] = cv2.resize(variables.TOOLBAR, (variables.TOOLBAR_WIDTH - 20, variables.TOOLBAR_HEIGHT - 20))

        frame = ui.ImageTk.PhotoImage(ui.Image.fromarray(frame))
        if last_frame != frame:
            ui.canvas.configure(image=frame)
            ui.canvas.image = frame
            last_frame = frame
        last_content = content

    variables.ROOT.update()

    time_to_sleep = 1/variables.FPS - (time.time() - start)
    if time_to_sleep > 0:
        time.sleep(time_to_sleep)

if settings.Get("Console", "HideConsole", False):
    console.RestoreConsole()
    console.CloseConsole()

SetMouseSpeed(variables.DEFAULT_MOUSE_SPEED)