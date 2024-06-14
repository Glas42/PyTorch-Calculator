import src.variables as variables
import src.settings as settings
import src.console as console
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

variables.MOUSE_DEFAULT_SPEED = ui.GetMouseSpeed()

ui.Initialize()

last_mouse_x = None
last_mouse_y = None

while variables.RUN:

    for event in ui.pygame.event.get():
        if event.type == ui.pygame.QUIT:
            variables.RUN = False
        elif event.type == ui.pygame.MOUSEWHEEL:
            if event.y > 0:
                print("Mouse wheel scrolled up")
            elif event.y < 0:
                print("Mouse wheel scrolled down")

    mouse_x, mouse_y = ui.pygame.mouse.get_pos()
    left_clicked, _, right_clicked = ui.pygame.mouse.get_pressed()
    if last_mouse_x is None: last_mouse_x = mouse_x
    if last_mouse_y is None: last_mouse_y = mouse_y

    if left_clicked:
        ui.pygame.draw.line(ui.pygame.display.get_surface(), (255, 255, 255), (last_mouse_x, last_mouse_y), (mouse_x, mouse_y), 3)

    last_mouse_x, last_mouse_y = mouse_x, mouse_y

    ui.Update()

if settings.Get("Console", "HideConsole", False):
    console.RestoreConsole()
    console.CloseConsole()

ui.SetMouseSpeed(variables.MOUSE_DEFAULT_SPEED)
ui.pygame.quit()
exit()