import src.variables as variables
import src.settings as settings
import src.console as console
import src.ui as ui

import traceback
import threading
import requests
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

current_tab = None
last_tab = None

def WindowMover():
    last_window_position = None
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
                    win32gui.SetWindowPos(variables.HWND, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                    if window_position[2] != last_window_position[2] or window_position[3] != last_window_position[3]:
                        ui.pygame.display.set_mode(size=(window_position[2] - 10, window_position[3] - 50), flags=ui.pygame.NOFRAME, vsync=True)
                        ui.frame.fill((250, 250, 250) if settings.Get("UI", "theme") == "light" else (28, 28, 28))
                        ui.pygame.display.update()
                last_window_position = window_position
        except:
            pass
        time_to_sleep = 1/60 - (time.time() - start)
        if time_to_sleep > 0:
            time.sleep(time_to_sleep)
threading.Thread(target=WindowMover, daemon=True).start()

while variables.BREAK == False:
    start = time.time()

    current_tab = ui.tabControl.tab(ui.tabControl.select(), "text")
    if current_tab == "Draw" and str(win32gui.GetWindowText(win32gui.GetForegroundWindow())) == variables.WINDOWNAME:
        if win32gui.GetWindowPlacement(variables.HWND)[1] != 1:
            win32gui.ShowWindow(variables.HWND, 1)
    elif win32gui.GetWindowPlacement(variables.HWND)[1] == 1:
        win32gui.ShowWindow(variables.HWND, 2)
    last_tab = current_tab

    variables.ROOT.update()
    ui.pygame.display.update()

    time_to_sleep = 1/60 - (time.time() - start)
    if time_to_sleep > 0:
        time.sleep(time_to_sleep)

if settings.Get("Console", "HideConsole", False):
    console.RestoreConsole()
    console.CloseConsole()