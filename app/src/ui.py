import src.uicomponents as uicomponents
import src.variables as variables
import src.settings as settings
import src.console as console

from PIL import Image, ImageTk
from tkinter import filedialog
from tkinter import ttk
import traceback
import tkinter
import sv_ttk
import numpy
import os

def initialize():
    global theme
    width = settings.Get("UI", "width", 1000)
    height = settings.Get("UI", "height", 600)
    x = settings.Get("UI", "x", 0)
    y = settings.Get("UI", "y", 0)
    theme = settings.Get("UI", "theme", "dark")
    resizable = settings.Get("UI", "resizable", False)

    variables.ROOT = tkinter.Tk()
    variables.ROOT.title(variables.WINDOWNAME)
    variables.ROOT.geometry(f"{width}x{height}+{x}+{y}")
    variables.ROOT.update()
    sv_ttk.set_theme(theme, variables.ROOT)
    variables.ROOT.protocol("WM_DELETE_WINDOW", close)
    variables.ROOT.resizable(resizable, resizable)
    variables.HWND = variables.ROOT.winfo_id()

    variables.CANVAS_DRAW_COLOR = (0, 0, 0) if theme == "light" else (255, 255, 255)

    if os.name == "nt":
        from ctypes import windll, byref, sizeof, c_int
        variables.HWND = windll.user32.GetParent(variables.ROOT.winfo_id())
        windll.dwmapi.DwmSetWindowAttribute(variables.HWND, 35, byref(c_int(0xE7E7E7 if theme == "light" else 0x2F2F2F)), sizeof(c_int))
        if theme == "light":
            variables.ROOT.iconbitmap(default=f"{variables.PATH}assets/icon_light.ico")
        else:
            variables.ROOT.iconbitmap(default=f"{variables.PATH}assets/icon_dark.ico")

    global background
    background = numpy.zeros((variables.ROOT.winfo_height() - 40, variables.ROOT.winfo_width(), 3), numpy.uint8)
    background[:] = ((250, 250, 250) if settings.Get("UI", "theme") == "light" else (28, 28, 28))

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


    global canvas
    canvas = tkinter.Label(tab_draw, image=ImageTk.PhotoImage(Image.fromarray(background)))
    canvas.grid(row=0, column=0, padx=0, pady=0, columnspan=2)


    global test_frame
    test_frame = numpy.zeros((40, 40, 3), numpy.uint8)
    test_frame[:] = (0, 255, 0)
    test_frame = ImageTk.PhotoImage(Image.fromarray(test_frame))

    global test
    test = tkinter.Label(tab_draw, image=test_frame, border=0, highlightthickness=0)
    test.grid(row=0, column=1, padx=10, pady=10, sticky="ne")


    def new():
        variables.CANVAS_POSITION = (settings.Get("UI", "width", 1000) - 10) // 2, (settings.Get("UI", "height", 600) - 50) // 2
        variables.CANVAS_ZOOM = 1
        variables.CANVAS_SHOW_GRID = True
        variables.CANVAS_GRID_TYPE = "DOT"
        variables.CANVAS_CONTENT = []
        variables.CANVAS_TEMP = []
        variables.CANVAS_DELETE_LIST = []
        variables.CANVAS_DRAW_COLOR = (0, 0, 0) if theme == "light" else (255, 255, 255)
        tabControl.select(tab_draw)
    uicomponents.MakeButton(tab_file, "New", new, row=0, column=0, padx=20, pady=20, sticky="nw")

    def save():
        try:
            variables.FILE_PATH = filedialog.asksaveasfilename(initialdir=settings.Get("Save", "LastDirectory", os.path.dirname(os.path.dirname(variables.PATH))), title="Select a path to save to", filetypes=((".txt","*.txt"), ("all files","*.*")))
            if variables.FILE_PATH == "":
                return
            settings.Set("Save", "LastDirectory", os.path.dirname(variables.FILE_PATH))
            if not variables.FILE_PATH.endswith(".txt"):
                variables.FILE_PATH += ".txt"
            with open(variables.FILE_PATH, "w") as f:
                f.write(f"""
                    {variables.CANVAS_POSITION}#
                    {variables.CANVAS_ZOOM}#
                    {variables.CANVAS_SHOW_GRID}#
                    {variables.CANVAS_GRID_TYPE}#
                    {variables.CANVAS_CONTENT}#
                    {variables.CANVAS_TEMP}#
                    {variables.CANVAS_DELETE_LIST}#
                    {variables.CANVAS_DRAW_COLOR}
                """.replace(" ", "").replace("\n", ""))
            tabControl.select(tab_draw)
        except:
            traceback.print_exc()
    uicomponents.MakeButton(tab_file, "Save", save, row=0, column=1, padx=20, pady=20, sticky="nw")

    def load():
        try:
            variables.FILE_PATH = filedialog.askopenfilename(initialdir=settings.Get("Load", "LastDirectory", os.path.dirname(os.path.dirname(variables.PATH))), title="Select a text file to load", filetypes=((".txt","*.txt"), ("all files","*.*")))
            if variables.FILE_PATH == "":
                return
            settings.Set("Load", "LastDirectory", os.path.dirname(variables.FILE_PATH))
            if not variables.FILE_PATH.endswith(".txt"):
                variables.FILE_PATH += ".txt"
            with open(variables.FILE_PATH, "r") as f:
                content = str(f.read()).split("#")
                variables.CANVAS_POSITION = eval(content[0])
                variables.CANVAS_ZOOM = float(content[1])
                variables.CANVAS_SHOW_GRID = bool(content[2])
                variables.CANVAS_GRID_TYPE = str(content[3])
                variables.CANVAS_CONTENT = eval(content[4])
                variables.CANVAS_TEMP = eval(content[5])
                variables.CANVAS_DELETE_LIST = eval(content[6])
                variables.CANVAS_DRAW_COLOR = eval(content[7])
            tabControl.select(tab_draw)
        except:
            traceback.print_exc()
    uicomponents.MakeButton(tab_file, "Load", load, row=0, column=2, padx=20, pady=20, sticky="nw")


    uicomponents.MakeLabel(tab_settings, "Theme:", row=0, column=0, padx=15, pady=10, sticky="nw", font=("Segoe UI", 11))
    def ChangeTheme(theme):
        settings.Set("UI", "theme", theme)
        sv_ttk.set_theme(theme, variables.ROOT)
        style = ttk.Style()
        style.layout("Tab",[('Notebook.tab',{'sticky':'nswe','children':[('Notebook.padding',{'side':'top','sticky':'nswe','children':[('Notebook.label',{'side':'top','sticky':''})],})],})])
        global background
        background[:] = ((250, 250, 250) if theme == "light" else (28, 28, 28))
        variables.CANVAS_DRAW_COLOR = (0, 0, 0) if theme == "light" else (255, 255, 255)
        if os.name == "nt":
            from ctypes import windll, byref, sizeof, c_int
            windll.dwmapi.DwmSetWindowAttribute(windll.user32.GetParent(variables.ROOT.winfo_id()), 35, byref(c_int(0xE7E7E7 if theme == "light" else 0x2F2F2F)), sizeof(c_int))
        if theme == "light":
            variables.ROOT.iconbitmap(default=f"{variables.PATH}assets/icon_light.ico")
        else:
            variables.ROOT.iconbitmap(default=f"{variables.PATH}assets/icon_dark.ico")
    theme = tkinter.StringVar(value=settings.Get("UI", "theme", "dark"))
    ttk.Radiobutton(tab_settings, text="Light", command=lambda: ChangeTheme("light"), variable=theme, value="light").grid(row=1, column=0, padx=20, sticky="nw")
    ttk.Radiobutton(tab_settings, text="Dark", command=lambda: ChangeTheme("dark"), variable=theme, value="dark").grid(row=2, column=0, padx=20, sticky="nw")

    uicomponents.MakeLabel(tab_settings, "\nGeneral Settings", row=3, column=0, padx=15, pady=10, sticky="nw", font=("Segoe UI", 11))

    uicomponents.MakeCheckButton(tab_settings, "Auto Update", "Update", "AutoUpdate", row=4, column=0, padx=20, pady=0, width=11)

    def ChangeHideConsole():
        if settings.Get("Console", "HideConsole"):
            console.HideConsole()
        else:
            console.RestoreConsole()
    uicomponents.MakeCheckButton(tab_settings, "Hide Console", "Console", "HideConsole", row=5, column=0, padx=20, pady=0, width=11, callback=lambda: ChangeHideConsole())

    def ChangeResizable():
        resizable = settings.Get("UI", "resizable", False)
        variables.ROOT.resizable(resizable, resizable)
        ChangeTheme(settings.Get("UI", "theme", "dark"))
    uicomponents.MakeCheckButton(tab_settings, "Resizeable", "UI", "resizable", row=6, column=0, padx=20, pady=0, width=11, callback=lambda: ChangeResizable())

    uicomponents.MakeLabel(tab_settings, "\nDraw Settings", row=7, column=0, padx=15, pady=10, sticky="nw", font=("Segoe UI", 11))

    uicomponents.MakeCheckButton(tab_settings, "Upscale Lines", "Draw", "UpscaleLines", row=8, column=0, padx=20, pady=0, width=11)
    uicomponents.MakeCheckButton(tab_settings, "Smooth Lines", "Draw", "SmoothLines", row=9, column=0, padx=20, pady=0, width=11)

    uicomponents.MakeLabel(tab_settings, "                     Mouse Slow-\n                     down Factor", row=10, column=0, padx=24, pady=0, sticky="w")
    MouseSlowdownSlider = tkinter.Scale(tab_settings, from_=0.1, to=1, resolution=0.01, orient=tkinter.HORIZONTAL, length=75, command=lambda x: settings.Set("Draw", "MouseSlowdown", float(x)))
    MouseSlowdownSlider.set(settings.Get("Draw", "MouseSlowdown", 1))
    MouseSlowdownSlider.grid(row=10, column=0, padx=21, pady=0, sticky="nw")