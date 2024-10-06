import src.translate as translate
import src.variables as variables
import src.keyboard as keyboard
import src.settings as settings
import src.console as console
import src.pytorch as pytorch
import src.updater as updater
import src.canvas as canvas
import src.mouse as mouse
import src.ui as ui

import time
import sys
import os

os.system("cls" if variables.OS == "nt" else "clear")
print("\nPyTorch-Calculator\n------------------\n")

if "--dev" in sys.argv:
    variables.DEVMODE = True

if os.path.exists(f"{variables.PATH}cache") == False:
    os.makedirs(f"{variables.PATH}cache")

if settings.Get("Console", "HideConsole", False):
    console.HideConsole()

translate.Initialize()
pytorch.CheckCuda()
ui.Initialize()
updater.CheckForUpdates()

mouse.Run()
keyboard.Run()

if variables.DEVMODE:
    import hashlib
    Scripts = []
    Scripts.append(("Main", f"{variables.PATH}app/main.py"))
    for Object in os.listdir(f"{variables.PATH}app/src"):
        Scripts.append((Object, f"{variables.PATH}app/src/{Object}"))
    LastScripts = {}
    for i, (Script, Path) in enumerate(Scripts):
        try:
            Hash = hashlib.md5(open(Path, "rb").read()).hexdigest()
            LastScripts[i] = Hash
        except:
            pass

while variables.BREAK == False:
    Start = time.time()

    if variables.DEVMODE:
        for i, (Script, Path) in enumerate(Scripts):
            try:
                Hash = hashlib.md5(open(Path, "rb").read()).hexdigest()
                if Hash != LastScripts[i]:
                    ui.Restart()
                    LastScripts[i] = Hash
                    break
            except:
                pass

    canvas.Update()

    ui.Update()

    TimeToSleep = 1/variables.FPS - (time.time() - Start)
    if TimeToSleep > 0:
        time.sleep(TimeToSleep)

if settings.Get("Console", "HideConsole", False):
    console.RestoreConsole()
    console.CloseConsole()

if variables.DEFAULT_MOUSE_SPEED != None:
    mouse.SetMouseSpeed(variables.DEFAULT_MOUSE_SPEED)