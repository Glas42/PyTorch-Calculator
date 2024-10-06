import src.variables as variables
import src.console as console
import ctypes

RED = "\033[91m"
NORMAL = "\033[0m"

def CrashReport(Type:str, Message:str, Additional=None):
    if Message.strip() == "":
        return
    console.RestoreConsole()
    if variables.DEFAULT_MOUSE_SPEED != None:
        Speed = variables.DEFAULT_MOUSE_SPEED
        if type(Speed) != int:
            return
        Speed = int(Speed)
        if Speed < 1:
            Speed = 1
        elif Speed > 20:
            Speed = 20
        ctypes.windll.user32.SystemParametersInfoA(113, 0, Speed, 0)
    while Message.endswith('\n'):
        Message = Message[:-1]
    if variables.DEVMODE == False:
        Message = f"{RED}>{NORMAL} " + Message.replace("\n", f"\n{RED}>{NORMAL} ")
    print(f"{RED}{Type}{NORMAL}\n{Message}\n")