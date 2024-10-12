from src.crashreport import CrashReport
import src.variables as variables

import SimpleWindow
import threading
import traceback
import ctypes
import time


def Run():
    def RunThread():
        try:
            LastLeftClicked, LastRightClicked = False, False
            LastCtrlZClicked, LastCtrlYClicked = False, False
            LastCtrlSClicked, LastCtrlNClicked = False, False
            LastCtrlCClicked, LastCtrlVClicked, LastCtrlXClicked, LastCtrlDClicked = False, False, False, False
            while variables.BREAK == False:
                Start = time.time()

                if SimpleWindow.GetWindowStatus(variables.NAME)["Foreground"] == False or variables.PAGE != "Canvas":
                    time.sleep(0.1)
                    continue

                CtrlZClicked = ctypes.windll.user32.GetKeyState(0x5A) & 0x8000 != 0
                CtrlYClicked = ctypes.windll.user32.GetKeyState(0x59) & 0x8000 != 0
                CtrlSClicked = ctypes.windll.user32.GetKeyState(0x53) & 0x8000 != 0
                CtrlNClicked = ctypes.windll.user32.GetKeyState(0x4E) & 0x8000 != 0
                CtrlCClicked = ctypes.windll.user32.GetKeyState(0x43) & 0x8000 != 0
                CtrlVClicked = ctypes.windll.user32.GetKeyState(0x56) & 0x8000 != 0
                CtrlXClicked = ctypes.windll.user32.GetKeyState(0x58) & 0x8000 != 0
                CtrlDClicked = ctypes.windll.user32.GetKeyState(0x44) & 0x8000 != 0

                if CtrlZClicked == True and LastCtrlZClicked == False:
                    if len(variables.CANVAS_CONTENT) > 0:
                        variables.CANVAS_DELETE_LIST.append(variables.CANVAS_CONTENT[-1])
                        variables.CANVAS_CONTENT.pop()

                if CtrlYClicked == True and LastCtrlYClicked == False:
                    if len(variables.CANVAS_DELETE_LIST) > 0:
                        variables.CANVAS_CONTENT.append(variables.CANVAS_DELETE_LIST[-1])
                        variables.CANVAS_DELETE_LIST.pop()

                LastCtrlZClicked = CtrlZClicked
                LastCtrlYClicked = CtrlYClicked
                LastCtrlSClicked = CtrlSClicked
                LastCtrlNClicked = CtrlNClicked
                LastCtrlCClicked = CtrlCClicked
                LastCtrlVClicked = CtrlVClicked
                LastCtrlXClicked = CtrlXClicked
                LastCtrlDClicked = CtrlDClicked

                TimeToSleep = 1/variables.FPS - (time.time() - Start)
                if TimeToSleep > 0:
                    time.sleep(TimeToSleep)
        except:
            CrashReport("Keyboard - Error in function RunThread.", str(traceback.format_exc()))

    threading.Thread(target=RunThread, daemon=True).start()