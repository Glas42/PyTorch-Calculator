import src.variables as variables
import src.settings as settings
import src.console as console
import src.mouse as mouse
import src.ui as ui

import traceback
import threading
import requests
import win32gui
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

ui.Initialize()

variables.HWND = None
top_windows = []
win32gui.EnumWindows(lambda hwnd, param: param.append((hwnd, win32gui.GetWindowText(hwnd))), top_windows)
variables.HWND = next((hwnd for hwnd, text in top_windows if variables.WINDOWNAME in text), None)

drawlist = None
drawlist1 = None

last_mouse_x = None
last_mouse_y = None

while variables.RUN:

    mouse_x, mouse_y, mouse_x_relative, mouse_y_relative, left_clicked, right_clicked, zoom = mouse.get_position()

    if drawlist is not None:
        ui.dpg.delete_item(drawlist)

    with ui.dpg.viewport_drawlist(label="draw") as drawlist:
        if last_mouse_x is not None and last_mouse_y is not None:
            ui.dpg.draw_circle([mouse_x, mouse_y], radius=2, color=[255, 255, 255, 255], fill=[255, 255, 255, 255])

    with ui.dpg.viewport_drawlist(label="draw1") as drawlist1:
        if last_mouse_x is not None and last_mouse_y is not None and left_clicked:
            ui.dpg.draw_line([mouse_x, mouse_y], [last_mouse_x, last_mouse_y], thickness=3, color=[255, 255, 255, 255])

    last_mouse_x, last_mouse_y = mouse_x, mouse_y

    ui.Update()

if settings.Get("Console", "HideConsole", False):
    console.RestoreConsole()
    console.CloseConsole()
mouse.set_speed(variables.MOUSE_DEFAULT_SPEED)