import src.variables as variables
import src.settings as settings
import src.console as console
import src.ui as ui

from pynput.mouse import Listener
import traceback
import threading
import requests
import win32gui
import ctypes
import mouse
import os

if settings.Get("Console", "HideConsole", False):
    console.HideConsole()

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
threading.Thread(target=update_check, daemon=True).start()


def get_current_speed():
    get_mouse_speed = 112   # 0x0070 for SPI_GETMOUSESPEED
    speed = ctypes.c_int()
    ctypes.windll.user32.SystemParametersInfoA(get_mouse_speed, 0, ctypes.byref(speed), 0)

    return speed.value
print(get_current_speed())
def change_speed(speed):
    #   1 - slow
    #   10 - standard
    #   20 - fast
    set_mouse_speed = 113   # 0x0071 for SPI_SETMOUSESPEED
    ctypes.windll.user32.SystemParametersInfoA(set_mouse_speed, 0, speed, 0)


def mouse_scroll_handler():
    def on_scroll(x, y, dx, dy):
        window_x, window_y, window_w, window_h = ui.dpg.get_viewport_pos()[0], ui.dpg.get_viewport_pos()[1], ui.dpg.get_viewport_width(), ui.dpg.get_viewport_height()
        if window_x < x < window_x + window_w and window_y < y < window_y + window_h:
            if ctypes.windll.user32.GetForegroundWindow() == ctypes.windll.user32.FindWindowW(None, variables.WINDOWNAME):
                global zoom
                zoom -= dy/100
    def on_click(x, y, button, pressed):
        window_x, window_y, window_w, window_h = ui.dpg.get_viewport_pos()[0], ui.dpg.get_viewport_pos()[1], ui.dpg.get_viewport_width(), ui.dpg.get_viewport_height()
        if window_x < x < window_x + window_w and window_y < y < window_y + window_h:
            if ctypes.windll.user32.GetForegroundWindow() == ctypes.windll.user32.FindWindowW(None, variables.WINDOWNAME):
                global left_clicked
                global right_clicked
                if str(button) == "Button.left":
                    left_clicked = pressed
                if pressed:
                    set_mouse_sensitivity(0.5)  # Set mouse sensitivity to half
                else:
                    set_mouse_sensitivity(1.0)  # Reset mouse sensitivity to normal
                if str(button) == "Button.right":
                    right_clicked = pressed
    with Listener(on_click=on_click, on_scroll=on_scroll) as listener:
        listener.join()
threading.Thread(target=mouse_scroll_handler, daemon=True).start()

zoom = 0
left_clicked = False
right_clicked = False
drawlist = None
drawlist1 = None
hwnd = None

last_mouse_x = None
last_mouse_y = None
last_window = None, None, None, None

ui.Initialize()
while variables.RUN:
    ui.Update()

    if hwnd == None:
        hwnd = None
        top_windows = []
        win32gui.EnumWindows(lambda hwnd, top_windows: top_windows.append((hwnd, win32gui.GetWindowText(hwnd))), top_windows)
        for hwnd, window_text in top_windows:
            if variables.WINDOWNAME in window_text:
                break

    try:
        mouse_x, mouse_y = mouse.get_position()
        rect = win32gui.GetClientRect(hwnd)
        tl = win32gui.ClientToScreen(hwnd, (rect[0], rect[1]))
        br = win32gui.ClientToScreen(hwnd, (rect[2], rect[3]))
        window_x, window_y, window_width, window_height = (tl[0], tl[1], br[0] - tl[0], br[1] - tl[1])
    except:
        if last_window != (None, None, None, None):
            window_x, window_y, window_width, window_height = last_window
        else:
            window_x = settings.Get("Window", "X", variables.SCREEN_WIDTH // 4)
            window_y = settings.Get("Window", "Y", variables.SCREEN_HEIGHT // 4)
            window_width = settings.Get("Window", "Width", variables.SCREEN_WIDTH // 2)
            window_height = settings.Get("Window", "Height", variables.SCREEN_HEIGHT // 2)

    mouse_x -= window_x
    mouse_y -= window_y

    if drawlist is not None:
        ui.dpg.delete_item(drawlist)

    with ui.dpg.viewport_drawlist(label="draw") as drawlist:
        if last_mouse_x is not None and last_mouse_y is not None:
            ui.dpg.draw_circle([mouse_x, mouse_y], radius=2, color=[255, 255, 255, 255], fill=[255, 255, 255, 255])

    with ui.dpg.viewport_drawlist(label="draw1") as drawlist1:
        if last_mouse_x is not None and last_mouse_y is not None and left_clicked:
            ui.dpg.draw_line([mouse_x, mouse_y], [last_mouse_x, last_mouse_y], thickness=3, color=[255, 255, 255, 255])

    last_mouse_x, last_mouse_y = mouse_x, mouse_y

if settings.Get("Console", "HideConsole", False):
    console.RestoreConsole()
    console.CloseConsole()
restore_default_mouse_sensitivity()