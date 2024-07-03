import src.uicomponents as uicomponents
import src.variables as variables
import src.settings as settings
import src.console as console

from tkinter import filedialog
from tkinter import ttk
import tkinter
import sv_ttk
import numpy
import cv2
import os

def initialize():
    global theme
    width = settings.Get("UI", "width", 1000)
    height = settings.Get("UI", "height", 600)
    x = settings.Get("UI", "x", 0)
    y = settings.Get("UI", "y", 0)
    theme = settings.Get("UI", "theme", "dark")
    resizable = settings.Get("UI", "resizable", False)
    if os.name == "nt":
        from ctypes import windll, byref, sizeof, c_int
        import win32gui, win32con

    variables.ROOT = tkinter.Tk()
    variables.ROOT.title(variables.WINDOWNAME)
    variables.ROOT.geometry(f"{width}x{height}+{x}+{y}")
    variables.ROOT.update()
    sv_ttk.set_theme(theme, variables.ROOT)
    variables.ROOT.protocol("WM_DELETE_WINDOW", close)
    variables.ROOT.resizable(resizable, resizable)
    variables.TK_HWND = variables.ROOT.winfo_id()

    if os.name == "nt":
        variables.HWND = windll.user32.GetParent(variables.ROOT.winfo_id())
        windll.dwmapi.DwmSetWindowAttribute(variables.HWND, 35, byref(c_int(0xE7E7E7 if theme == "light" else 0x2F2F2F)), sizeof(c_int))
        if theme == "light":
            variables.ROOT.iconbitmap(default=f"{variables.PATH}assets/icon_light.ico")
        else:
            variables.ROOT.iconbitmap(default=f"{variables.PATH}assets/icon_dark.ico")

    rect = win32gui.GetClientRect(variables.TK_HWND)
    tl = win32gui.ClientToScreen(variables.TK_HWND, (rect[0], rect[1]))
    br = win32gui.ClientToScreen(variables.TK_HWND, (rect[2], rect[3]))
    window_position = (tl[0], tl[1], br[0] - tl[0], br[1] - tl[1])
    cv2.namedWindow(variables.WINDOWNAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(variables.WINDOWNAME, window_position[2] - 10, window_position[3] - 50)
    cv2.moveWindow(variables.WINDOWNAME, window_position[0] + 5, window_position[1] + 45)
    cv2.setWindowProperty(variables.WINDOWNAME, cv2.WND_PROP_TOPMOST, 1)
    cv2.setWindowProperty(variables.WINDOWNAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    variables.HWND = win32gui.FindWindow(None, variables.WINDOWNAME)
    win32gui.SetWindowLong(variables.HWND, win32con.GWL_EXSTYLE, win32gui.GetWindowLong(variables.HWND, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)

    global background
    background = numpy.zeros((settings.Get("UI", "height", 600), settings.Get("UI", "width", 1000), 3), numpy.uint8)
    background[:] = ((250, 250, 250) if settings.Get("UI", "theme") == "light" else (28, 28, 28))

    if variables.OS == "nt":
        windll.dwmapi.DwmSetWindowAttribute(variables.HWND, 35, byref(c_int(0x000000)), sizeof(c_int))
        if theme == "light":
            hicon = win32gui.LoadImage(None, f"{variables.PATH}assets/icon_light.ico", win32con.IMAGE_ICON, 0, 0, win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE)
        else:
            hicon = win32gui.LoadImage(None, f"{variables.PATH}assets/icon_dark.ico", win32con.IMAGE_ICON, 0, 0, win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE)
        win32gui.SendMessage(variables.HWND, win32con.WM_SETICON, win32con.ICON_SMALL, hicon)
        win32gui.SendMessage(variables.HWND, win32con.WM_SETICON, win32con.ICON_BIG, hicon)

def close():
    settings.Set("UI", "width", variables.ROOT.winfo_width())
    settings.Set("UI", "height", variables.ROOT.winfo_height())
    settings.Set("UI", "x", variables.ROOT.winfo_x())
    settings.Set("UI", "y", variables.ROOT.winfo_y())
    console.RestoreConsole()
    console.CloseConsole()
    variables.ROOT.destroy()
    variables.BREAK = True

def createUI():
    style = ttk.Style()
    style.layout("Tab",[('Notebook.tab',{'sticky':'nswe','children':[('Notebook.padding',{'side':'top','sticky':'nswe','children':[('Notebook.label',{'side':'top','sticky':''})],})],})])

    global tabControl
    tabControl = ttk.Notebook(variables.ROOT)
    tabControl.pack(expand = 1, fill="both")

    tab_draw = ttk.Frame(tabControl)
    tab_draw.grid_rowconfigure(0, weight=1)
    tab_draw.grid_columnconfigure(0, weight=1)
    tabControl.add(tab_draw, text='Draw')

    tab_file = ttk.Frame(tabControl)
    tabControl.add(tab_file, text='File')

    tab_settings = ttk.Frame(tabControl)
    tabControl.add(tab_settings, text='Settings')


    uicomponents.MakeLabel(tab_draw, "The drawing window is hidden, it will be shown again when you return back to the application.", row=0, column=0, sticky="ns")


    global save
    def save():
        variables.FILE_PATH = filedialog.asksaveasfilename(initialdir=os.path.dirname(os.path.dirname(variables.PATH)), title="Select a path to save to", filetypes=((".txt","*.txt"), ("all files","*.*")))
        if variables.FILE_PATH == "":
            return
        if not variables.FILE_PATH.endswith(".txt"):
            variables.FILE_PATH += ".txt"
        with open(variables.FILE_PATH, "w") as f:
            f.write(str(variables.FILE_CONTENT))
    uicomponents.MakeButton(tab_file, "Save", save, row=0, column=0, padx=20, pady=20, sticky="nw")

    global load
    def load():
        variables.FILE_PATH = filedialog.askopenfilename(initialdir=os.path.dirname(os.path.dirname(variables.PATH)), title="Select a text file to load", filetypes=((".txt","*.txt"), ("all files","*.*")))
        if variables.FILE_PATH == "":
            return
        if not variables.FILE_PATH.endswith(".txt"):
            variables.FILE_PATH += ".txt"
        with open(variables.FILE_PATH, "r") as f:
            variables.FILE_CONTENT = eval(f.read())
    uicomponents.MakeButton(tab_file, "Load", load, row=0, column=1, padx=20, pady=20, sticky="nw")


    uicomponents.MakeLabel(tab_settings, "Set the theme:", row=0, column=0, padx=20, pady=20, sticky="nw", font=("Segoe UI", 11))
    def ChangeTheme(theme):
        settings.Set("UI", "theme", theme)
        sv_ttk.set_theme(theme, variables.ROOT)
        style = ttk.Style()
        style.layout("Tab",[('Notebook.tab',{'sticky':'nswe','children':[('Notebook.padding',{'side':'top','sticky':'nswe','children':[('Notebook.label',{'side':'top','sticky':''})],})],})])
        if variables.OS == "nt":
            import win32gui
            global background
            rect = win32gui.GetClientRect(variables.TK_HWND)
            tl = win32gui.ClientToScreen(variables.TK_HWND, (rect[0], rect[1]))
            br = win32gui.ClientToScreen(variables.TK_HWND, (rect[2], rect[3]))
            window_position = (tl[0], tl[1], br[0] - tl[0], br[1] - tl[1])
            win32gui.MoveWindow(variables.HWND, window_position[0] + 5, window_position[1] + 45, window_position[2] - 10, window_position[3] - 50, True)
            background = numpy.zeros((window_position[3] - 50, window_position[2] - 10, 3), numpy.uint8)
            background[:] = ((250, 250, 250) if settings.Get("UI", "theme") == "light" else (28, 28, 28))
        if os.name == "nt":
            from ctypes import windll, byref, sizeof, c_int
            windll.dwmapi.DwmSetWindowAttribute(windll.user32.GetParent(variables.ROOT.winfo_id()), 35, byref(c_int(0xE7E7E7 if theme == "light" else 0x2F2F2F)), sizeof(c_int))
            if theme == "light":
                variables.ROOT.iconbitmap(default=f"{variables.PATH}assets/icon_light.ico")
            else:
                variables.ROOT.iconbitmap(default=f"{variables.PATH}assets/icon_dark.ico")
    theme = tkinter.StringVar(value=settings.Get("UI", "theme", "dark"))
    ttk.Radiobutton(tab_settings, text="Dark", command=lambda: ChangeTheme("dark"), variable=theme, value="dark").grid(row=0, column=1)
    ttk.Radiobutton(tab_settings, text="Light", command=lambda: ChangeTheme("light"), variable=theme, value="light").grid(row=0, column=2)

    def ChangeResizable():
        resizable = settings.Get("UI", "resizable", False)
        variables.ROOT.resizable(resizable, resizable)
        ChangeTheme(settings.Get("UI", "theme", "dark"))
    uicomponents.MakeCheckButton(tab_settings, "Resizeable", "UI", "resizable", row=1, column=0, padx=20, pady=0, width=10, callback=lambda: ChangeResizable())

    def ChangeHideConsole():
        if settings.Get("Console", "HideConsole"):
            console.HideConsole()
        else:
            console.RestoreConsole()
    uicomponents.MakeCheckButton(tab_settings, "Hide Console", "Console", "HideConsole", row=2, column=0, padx=20, pady=0, width=10, callback=lambda: ChangeHideConsole())