import src.variables as variables
import src.settings as settings
import src.console as console
import src.mouse as mouse

import dearpygui.dearpygui as dpg

def Initialize():
    try:
        dpg.create_context()
        dpg.create_viewport(title=variables.WINDOWNAME,
                            always_on_top=False,
                            decorated=True,
                            resizable=True,
                            clear_color=[0, 0, 0, 255],
                            vsync=True,
                            x_pos=settings.Get("Window", "X", variables.SCREEN_WIDTH // 4),
                            y_pos=settings.Get("Window", "Y", variables.SCREEN_HEIGHT // 4),
                            width=settings.Get("Window", "Width", variables.SCREEN_WIDTH // 2),
                            height=settings.Get("Window", "Height", variables.SCREEN_HEIGHT // 2),
                            small_icon=f"{variables.PATH}icon.ico",
                            large_icon=f"{variables.PATH}icon.ico")
        dpg.setup_dearpygui()
        dpg.show_viewport()

        if variables.OS == "nt":
            import win32gui, win32con
            from ctypes import windll, byref, sizeof, c_int
            hwnd = win32gui.FindWindow(None, variables.WINDOWNAME)
            windll.dwmapi.DwmSetWindowAttribute(hwnd, 35, byref(c_int(0x000000)), sizeof(c_int))
    except:
        import traceback
        print(traceback.format_exc())

def Update():
    if dpg.is_dearpygui_running() == False:
        variables.RUN = False
        settings.Set("Window", "X", dpg.get_viewport_pos()[0])
        settings.Set("Window", "Y", dpg.get_viewport_pos()[1])
        settings.Set("Window", "Width", dpg.get_viewport_width())
        settings.Set("Window", "Height", dpg.get_viewport_height())
        if settings.Get("Console", "HideConsole", False):
            console.RestoreConsole()
            console.CloseConsole()
            mouse.set_speed(variables.MOUSE_DEFAULT_SPEED)
    dpg.render_dearpygui_frame()