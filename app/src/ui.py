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
import cv2
import os

def Initialize():
    width = settings.Get("UI", "width", 1000)
    height = settings.Get("UI", "height", 600)
    x = settings.Get("UI", "x", 0)
    y = settings.Get("UI", "y", 0)
    variables.THEME = settings.Get("UI", "theme", "dark")
    resizable = settings.Get("UI", "resizable", False)

    variables.ROOT = tkinter.Tk()
    variables.ROOT.title(variables.WINDOWNAME)
    variables.ROOT.geometry(f"{width}x{height}+{x}+{y}")
    variables.ROOT.update()
    sv_ttk.set_theme(variables.THEME, variables.ROOT)
    variables.ROOT.protocol("WM_DELETE_WINDOW", Close)
    variables.ROOT.resizable(resizable, resizable)
    variables.HWND = variables.ROOT.winfo_id()

    variables.CANVAS_DRAW_COLOR = (0, 0, 0) if variables.THEME == "light" else (255, 255, 255)

    if os.name == "nt":
        from ctypes import windll, byref, sizeof, c_int
        variables.HWND = windll.user32.GetParent(variables.ROOT.winfo_id())
        windll.dwmapi.DwmSetWindowAttribute(variables.HWND, 35, byref(c_int(0xE7E7E7 if variables.THEME == "light" else 0x2F2F2F)), sizeof(c_int))
        if variables.THEME == "light":
            variables.ROOT.iconbitmap(default=f"{variables.PATH}assets/icon_light.ico")
        else:
            variables.ROOT.iconbitmap(default=f"{variables.PATH}assets/icon_dark.ico")

    global background
    background = numpy.zeros((variables.ROOT.winfo_height() - 40, variables.ROOT.winfo_width(), 3), numpy.uint8)
    background[:] = ((250, 250, 250) if variables.THEME == "light" else (28, 28, 28))

def Close():
    settings.Set("UI", "width", variables.ROOT.winfo_width())
    settings.Set("UI", "height", variables.ROOT.winfo_height())
    settings.Set("UI", "x", variables.ROOT.winfo_x())
    settings.Set("UI", "y", variables.ROOT.winfo_y())
    console.RestoreConsole()
    console.CloseConsole()
    variables.ROOT.destroy()
    variables.BREAK = True


def CreateUI():
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


    global tools
    tools_icon = ImageTk.PhotoImage(Image.fromarray(numpy.zeros((20, 20, 3), numpy.uint8)))
    tools = tkinter.Label(tabControl, image=tools_icon, border=0, highlightthickness=0)
    tools.pack(anchor="e", padx=10, pady=10)


    global canvas
    canvas = tkinter.Label(tab_draw, image=ImageTk.PhotoImage(Image.fromarray(background)))
    canvas.grid(row=0, column=0, padx=0, pady=0, columnspan=2)


    def New():
        variables.CANVAS_POSITION = (settings.Get("UI", "width", 1000) - 10) // 2, (settings.Get("UI", "height", 600) - 50) // 2
        variables.CANVAS_ZOOM = 1
        variables.CANVAS_SHOW_GRID = True
        variables.CANVAS_GRID_TYPE = "DOT"
        variables.CANVAS_CONTENT = []
        variables.CANVAS_TEMP = []
        variables.CANVAS_DELETE_LIST = []
        variables.CANVAS_DRAW_COLOR = (0, 0, 0) if variables.THEME == "light" else (255, 255, 255)
        tabControl.select(tab_draw)
    uicomponents.MakeButton(tab_file, "New", New, row=0, column=0, padx=20, pady=20, sticky="nw")

    def Save():
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
    uicomponents.MakeButton(tab_file, "Save", Save, row=0, column=1, padx=20, pady=20, sticky="nw")

    def Load():
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
    uicomponents.MakeButton(tab_file, "Load", Load, row=0, column=2, padx=20, pady=20, sticky="nw")


    uicomponents.MakeLabel(tab_settings, "Theme:", row=0, column=0, padx=15, pady=10, sticky="nw", font=("Segoe UI", 11))
    def ChangeTheme(theme):
        variables.THEME = theme
        settings.Set("UI", "theme", variables.THEME)
        LoadToolBar()
        sv_ttk.set_theme(variables.THEME, variables.ROOT)
        style = ttk.Style()
        style.layout("Tab",[('Notebook.tab',{'sticky':'nswe','children':[('Notebook.padding',{'side':'top','sticky':'nswe','children':[('Notebook.label',{'side':'top','sticky':''})],})],})])
        global background
        background[:] = ((250, 250, 250) if variables.THEME == "light" else (28, 28, 28))
        variables.CANVAS_DRAW_COLOR = (0, 0, 0) if variables.THEME == "light" else (255, 255, 255)
        if os.name == "nt":
            from ctypes import windll, byref, sizeof, c_int
            windll.dwmapi.DwmSetWindowAttribute(windll.user32.GetParent(variables.ROOT.winfo_id()), 35, byref(c_int(0xE7E7E7 if variables.THEME == "light" else 0x2F2F2F)), sizeof(c_int))
        if variables.THEME == "light":
            variables.ROOT.iconbitmap(default=f"{variables.PATH}assets/icon_light.ico")
        else:
            variables.ROOT.iconbitmap(default=f"{variables.PATH}assets/icon_dark.ico")
    theme = tkinter.StringVar(value=variables.THEME)
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
        ChangeTheme(variables.THEME)
    uicomponents.MakeCheckButton(tab_settings, "Resizeable", "UI", "resizable", row=6, column=0, padx=20, pady=0, width=11, callback=lambda: ChangeResizable())

    uicomponents.MakeLabel(tab_settings, "\nDraw Settings", row=7, column=0, padx=15, pady=10, sticky="nw", font=("Segoe UI", 11))

    uicomponents.MakeCheckButton(tab_settings, "Upscale Lines", "Draw", "UpscaleLines", row=8, column=0, padx=20, pady=0, width=11)
    uicomponents.MakeCheckButton(tab_settings, "Smooth Lines", "Draw", "SmoothLines", row=9, column=0, padx=20, pady=0, width=11)

    uicomponents.MakeLabel(tab_settings, "                     Mouse Slow-\n                     down Factor", row=10, column=0, padx=24, pady=0, sticky="w")
    MouseSlowdownSlider = tkinter.Scale(tab_settings, from_=0.1, to=1, resolution=0.01, orient=tkinter.HORIZONTAL, length=75, command=lambda x: settings.Set("Draw", "MouseSlowdown", float(x)))
    MouseSlowdownSlider.set(settings.Get("Draw", "MouseSlowdown", 1))
    MouseSlowdownSlider.grid(row=10, column=0, padx=21, pady=0, sticky="nw")


def LoadToolBar():
    global tools_icon
    global tools_placeholder
    tools_icon = cv2.resize(cv2.imread(f'{variables.PATH}assets/pen_{variables.THEME}.png', cv2.IMREAD_UNCHANGED), (20, 20))
    for x in range(tools_icon.shape[1]):
        for y in range(tools_icon.shape[0]):
            if tools_icon[x][y][3] == 0:
                tools_icon[x][y] = (231, 231, 231, 255) if variables.THEME == "light" else (47, 47, 47, 255)
    tools_icon = tools_icon[:, :, :3]
    tools_icon = ImageTk.PhotoImage(Image.fromarray(tools_icon))
    tools_placeholder = numpy.zeros((20, 20, 3), numpy.uint8)
    tools_placeholder[:] = (231, 231, 231) if variables.THEME == "light" else (47, 47, 47)
    tools_placeholder = ImageTk.PhotoImage(Image.fromarray(tools_placeholder))

    def LoadToolbarIcon(name="", size=(25, 25)):
        if os.path.exists(f'{variables.PATH}assets/{name.lower()}_{variables.THEME}.png'):
            icon = cv2.resize(cv2.imread(f'{variables.PATH}assets/{name.lower()}_{variables.THEME}.png', cv2.IMREAD_UNCHANGED), size)
            for x in range(icon.shape[1]):
                for y in range(icon.shape[0]):
                    if icon[x][y][3] == 0:
                        icon[x][y] = (231, 231, 231, 255) if variables.THEME == "light" else (47, 47, 47, 255)
            icon = icon[:, :, :3]
            return icon
    home_icon = LoadToolbarIcon("home")
    ai_icon = LoadToolbarIcon("ai")
    grid_line_icon = LoadToolbarIcon("grid_line")
    grid_dot_icon = LoadToolbarIcon("grid_dot")
    rectangle_icon = LoadToolbarIcon("rectangle")
    circle_icon = LoadToolbarIcon("circle")
    graph_icon = LoadToolbarIcon("graph")
    color_icon = LoadToolbarIcon("color")
    text_icon = LoadToolbarIcon("text")

    def GenerateGridImage(images=[], columns=1, padding=10):
        columns = len(images)
        avg_resolution = 0, 0
        for image in images:
            avg_resolution = (avg_resolution[0] + image.shape[1], avg_resolution[1] + image.shape[0])
        avg_resolution = (avg_resolution[0] / len(images), avg_resolution[1] / len(images))
        temp = []
        for image in images:
            temp.append(cv2.resize(image, (round(avg_resolution[0]), round(avg_resolution[1]))))
        images = temp
        rows = (len(images) + columns - 1) // columns
        image = numpy.zeros((round(avg_resolution[1]) * rows + padding * (rows - 1), round(avg_resolution[0]) * columns + padding * (columns - 1), 3), numpy.uint8)
        image[:] = (231, 231, 231) if variables.THEME == "light" else (47, 47, 47)
        x = 0
        y = 0
        for i, img in enumerate(images):
            image[y:y+img.shape[0], x:x+img.shape[1]] = img
            x += round(avg_resolution[0]) + padding
            if (i + 1) % columns == 0:
                x = 0
                y += round(avg_resolution[1]) + padding
        return image
    variables.TOOLBAR = GenerateGridImage((home_icon, ai_icon, grid_line_icon, grid_dot_icon, rectangle_icon, circle_icon, graph_icon, color_icon, text_icon), 3, 10)
    variables.TOOLBAR_HEIGHT = variables.TOOLBAR.shape[0] + 20
    variables.TOOLBAR_WIDTH = variables.TOOLBAR.shape[1] + 20
    variables.ROOT.minsize(variables.TOOLBAR_WIDTH + 20, variables.TOOLBAR_HEIGHT + 60)
    if tabControl.tab(tabControl.select(), "text") == "Draw":
        tools.configure(image=tools_icon)
        tools.image = tools_icon
    else:
        tools.configure(image=tools_placeholder)
        tools.image = tools_placeholder