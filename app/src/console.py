import src.variables as variables
import traceback

if variables.OS == "nt":
    import win32gui, win32con, win32console
    import ctypes

RED = "\033[91m"
NORMAL = "\033[0m"

def RestoreConsole():
    try:
        if variables.OS == "nt":
            if variables.CONSOLEHWND != None and variables.CONSOLENAME != None:
                win32gui.ShowWindow(variables.CONSOLEHWND, win32con.SW_RESTORE)
            else:
                variables.CONSOLENAME = win32console.GetConsoleTitle()
                variables.CONSOLEHWND = win32gui.FindWindow(None, str(variables.CONSOLENAME))
                win32gui.ShowWindow(variables.CONSOLEHWND, win32con.SW_RESTORE)
    except:
        Type = "\nConsole - Restore Error."
        Message = str(traceback.format_exc())
        while Message.endswith('\n'):
            Message = Message[:-1]
        if variables.DEVMODE == False:
            Message = f"{RED}>{NORMAL} " + Message.replace("\n", f"\n{RED}>{NORMAL} ")
        print(f"{RED}{Type}{NORMAL}\n{Message}\n")

def HideConsole():
    try:
        if variables.OS == "nt":
            if variables.CONSOLEHWND != None and variables.CONSOLENAME != None:
                win32gui.ShowWindow(variables.CONSOLEHWND, win32con.SW_HIDE)
            else:
                variables.CONSOLENAME = win32console.GetConsoleTitle()
                variables.CONSOLEHWND = win32gui.FindWindow(None, str(variables.CONSOLENAME))
                win32gui.ShowWindow(variables.CONSOLEHWND, win32con.SW_HIDE)
    except:
        Type = "\nConsole - Hide Error."
        Message = str(traceback.format_exc())
        while Message.endswith('\n'):
            Message = Message[:-1]
        if variables.DEVMODE == False:
            Message = f"{RED}>{NORMAL} " + Message.replace("\n", f"\n{RED}>{NORMAL} ")
        print(f"{RED}{Type}{NORMAL}\n{Message}\n")

def CloseConsole():
    try:
        if variables.OS == "nt":
            if variables.CONSOLEHWND != None and variables.CONSOLENAME != None:
                ctypes.windll.user32.PostMessageW(variables.CONSOLEHWND, 0x10, 0, 0)
            else:
                variables.CONSOLENAME = win32console.GetConsoleTitle()
                variables.CONSOLEHWND = win32gui.FindWindow(None, str(variables.CONSOLENAME))
                ctypes.windll.user32.PostMessageW(variables.CONSOLEHWND, 0x10, 0, 0)
    except:
        Type = "\nConsole - Close Error."
        Message = str(traceback.format_exc())
        while Message.endswith('\n'):
            Message = Message[:-1]
        if variables.DEVMODE == False:
            Message = f"{RED}>{NORMAL} " + Message.replace("\n", f"\n{RED}>{NORMAL} ")
        print(f"{RED}{Type}{NORMAL}\n{Message}\n")