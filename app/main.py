import src.variables as variables
import src.settings as settings
import src.console as console
import src.ui as ui

import traceback
import threading
import requests
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
while variables.RUN:
    ui.Update()

if settings.Get("Console", "HideConsole", False):
    console.RestoreConsole()
    console.CloseConsole()