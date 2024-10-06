import src.translate as translate
import src.variables as variables
import src.settings as settings
import src.console as console
import src.pytorch as pytorch
import src.updater as updater
import src.ui as ui

import time
import sys
import os


if __name__ == '__main__':
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

    if variables.DEVMODE:
        import hashlib
        Scripts = []
        Scripts.append(("Main", f"{variables.PATH}app/main.py"))
        for Object in os.listdir(f"{variables.PATH}app/plugins"):
            Scripts.append((Object, f"{variables.PATH}app/plugins/{Object}/main.py"))
        for Object in os.listdir(f"{variables.PATH}app/modules"):
            Scripts.append((Object, f"{variables.PATH}app/modules/{Object}/main.py"))
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
                        if "plugins" in os.path.dirname(Path):
                            os.system("cls" if variables.OS == "nt" else "clear")
                            print("\nPyTorch-Calculator\n------------------\n")
                        elif "modules" in os.path.dirname(Path):
                            os.system("cls" if variables.OS == "nt" else "clear")
                            print("\nPyTorch-Calculator\n------------------\n")
                        else:
                            ui.Restart()
                        LastScripts[i] = Hash
                        break
                except:
                    pass

        ui.Update()

        TimeToSleep = 1/60 - (time.time() - Start)
        if TimeToSleep > 0:
            time.sleep(TimeToSleep)

    if settings.Get("Console", "HideConsole", False):
        console.RestoreConsole()
        console.CloseConsole()