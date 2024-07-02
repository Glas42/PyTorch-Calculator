import src.settings as settings
from tkinter import ttk
import tkinter as tk

def MakeButton(parent, text:str, command, row:int, column:int, style:str="TButton", width:int=15, center:bool=False, padx:int=5, pady:int=5, state:str="!disabled", columnspan:int=1, rowspan:int=1, sticky:str="n"):

    button = ttk.Button(parent, text=text, command=command, style=style, padding=10, width=width, state=state)
    if not center:
        button.grid(row=row, column=column, padx=padx, pady=pady, columnspan=columnspan, rowspan=rowspan, sticky=sticky)
    else:
        button.grid(row=row, column=column, padx=padx, pady=pady, sticky="n", columnspan=columnspan, rowspan=rowspan)

    return button


def MakeCheckButton(parent, text:str, category:str, setting:str, row:int, column:int, width:int=17, padx:int=5, pady:int=5, values=[True, False], default=False, columnspan:int=1, callback=None):

    variable = tk.BooleanVar()
    value = settings.Get(category, setting)

    if value == None:
        value = default
        settings.Set(category, setting, value)
        variable.set(value)
    else:
        variable.set(value)

    if callback != None:
        def ButtonPressed():
            settings.Set(category, setting, values[0] if variable.get() else values[1])
            callback()
    else:
        def ButtonPressed():
            settings.Set(category, setting, values[0] if variable.get() else values[1])

    button = ttk.Checkbutton(parent, text=text, variable=variable, command=lambda: ButtonPressed(), width=width)
    button.grid(row=row, column=column, padx=padx, pady=pady, sticky="w", columnspan=columnspan)

    return variable


def MakeComboEntry(parent, text:str, category:str, setting:str, row: int, column: int, width: int=10, padx: int=5, pady: int=5, labelwidth:int=15, isFloat:bool=False, isString:bool=False, value="", sticky:str="w", labelSticky:str="w", labelPadX:int=10):

    label = ttk.Label(parent, text=text, width=labelwidth).grid(row=row, column=column, sticky=labelSticky, padx=labelPadX)

    if not isFloat and not isString:
        var = tk.IntVar()

        setting = settings.Get(category, setting)
        if setting == None:
            var.set(value)
            settings.Set(category, setting, value)
        else:
            var.set(setting)

    elif isString:
        var = tk.StringVar()
        
        setting = settings.Get(category, setting)
        if setting == None:
            var.set(value)
            settings.Set(category, setting, value)
        else:
            var.set(setting)

    else:
        var = tk.DoubleVar()

        setting = settings.Get(category, setting)
        if setting == None:
            var.set(value)
            settings.Set(category, setting, value)
        else:
            var.set(setting)

    entry = ttk.Entry(parent, textvariable=var, width=width, validatecommand=lambda: settings.Create(category, setting, var.get())).grid(row=row, column=column+1, sticky=sticky, padx=padx, pady=pady)

    return var


def MakeEntry(parent, row: int, column: int, width: int=10, padx: int=5, pady: int=5, isFloat:bool=False, isString:bool=False, value="", sticky:str="w"):

    if not isFloat and not isString:
        var = tk.IntVar()

    elif isString:
        var = tk.StringVar()

    else:
        var = tk.DoubleVar()

    entry = ttk.Entry(parent, textvariable=var, width=width).grid(row=row, column=column+1, sticky=sticky, padx=padx, pady=pady)

    return var

def MakeLabel(parent, text:str, row:int, column:int, font=("Segoe UI", 10), pady:int=5, padx:int=5, columnspan:int=1, sticky:str="n", fg:str="", bg:str=""):

    if text == "":
        var = tk.StringVar()
        var.set(text)

        if fg != "" and bg != "":
            label = ttk.Label(parent, font=font, textvariable=var, background=bg, foreground=fg)
        elif fg != "":
            label = ttk.Label(parent, font=font, textvariable=var, foreground=fg)
        elif bg != "":
            label = ttk.Label(parent, font=font, textvariable=var, background=bg)
        else: 
            label = ttk.Label(parent, font=font, textvariable=var)

        label.grid(row=row, column=column, columnspan=columnspan, padx=padx, pady=pady, sticky=sticky)

        return var
    else:
        if fg != "" and bg != "":
            label = ttk.Label(parent, font=font, text=text, background=bg, foreground=fg)
        elif fg != "":
            label = ttk.Label(parent, font=font, text=text, foreground=fg)
        elif bg != "":
            label = ttk.Label(parent, font=font, text=text, background=bg)
        else:
            label = ttk.Label(parent, font=font, text=text)

        label.grid(row=row, column=column, columnspan=columnspan, padx=padx, pady=pady, sticky=sticky)

        return label