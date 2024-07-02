import src.uicomponents as uicomponents
import src.variables as variables
import src.settings as settings
import src.console as console

from tkinter import ttk
import tkinter
import sv_ttk
import os

def initialize():
    width = settings.Get("UI", "width", 1000)
    height = settings.Get("UI", "height", 600)
    x = settings.Get("UI", "x", 0)
    y = settings.Get("UI", "y", 0)
    theme = settings.Get("UI", "theme", "dark")
    resizable = settings.Get("UI", "resizable", False)
    if os.name == "nt":
        from ctypes import windll, byref, sizeof, c_int

    variables.ROOT = tkinter.Tk()
    variables.ROOT.title("PyTorch-Calculator")
    variables.ROOT.geometry(f"{width}x{height}+{x}+{y}")
    variables.ROOT.update()
    sv_ttk.set_theme(theme, variables.ROOT)
    variables.ROOT.protocol("WM_DELETE_WINDOW", close)
    variables.ROOT.resizable(resizable, resizable)

    if os.name == "nt":
        variables.HWND = windll.user32.GetParent(variables.ROOT.winfo_id())
        windll.dwmapi.DwmSetWindowAttribute(variables.HWND, 35, byref(c_int(0xE7E7E7 if theme == "light" else 0x2F2F2F)), sizeof(c_int))
        if theme == "light":
            variables.ROOT.iconbitmap(default=f"{variables.PATH}assets/icon_light.ico")
        else:
            variables.ROOT.iconbitmap(default=f"{variables.PATH}assets/icon_dark.ico")

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

    tabControl = ttk.Notebook(variables.ROOT)
    tabControl.pack(expand = 1, fill ="both")

    tab_draw = ttk.Frame(tabControl)
    tabControl.add(tab_draw, text ='Draw')

    tab_settings = ttk.Frame(tabControl)
    tabControl.add(tab_settings, text ='Settings')


    uicomponents.MakeLabel(tab_settings, "Set the theme:", row=0, column=0, padx=20, pady=20, sticky="nw", font=("Segoe UI", 11))
    def ChangeTheme(theme):
        settings.Set("UI", "theme", theme)
        sv_ttk.set_theme(theme, variables.ROOT)
        if os.name == "nt":
            from ctypes import windll, byref, sizeof, c_int
            variables.HWND = windll.user32.GetParent(variables.ROOT.winfo_id())
            windll.dwmapi.DwmSetWindowAttribute(variables.HWND, 35, byref(c_int(0xE7E7E7 if theme == "light" else 0x2F2F2F)), sizeof(c_int))
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