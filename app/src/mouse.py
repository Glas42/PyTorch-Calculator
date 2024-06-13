import src.variables as variables
import src.settings as settings
import src.ui as ui

from pynput.mouse import Listener
import threading
import win32gui
import ctypes
import mouse

zoom = 0
left_clicked = False
right_clicked = False

mouse_slowed = False
last_mouse_x = None
last_mouse_y = None
last_window = None, None, None, None

def mouse_handler():
    def on_scroll(x, y, dx, dy):
        window_x, window_y, window_w, window_h = ui.dpg.get_viewport_pos()[0], ui.dpg.get_viewport_pos()[1], ui.dpg.get_viewport_width(), ui.dpg.get_viewport_height()
        if window_x < x < window_x + window_w and window_y < y < window_y + window_h:
            if ctypes.windll.user32.GetForegroundWindow() == ctypes.windll.user32.FindWindowW(None, variables.WINDOWNAME):
                global zoom
                zoom -= dy/100
    def on_click(x, y, button, pressed):
        window_x, window_y, window_w, window_h = ui.dpg.get_viewport_pos()[0], ui.dpg.get_viewport_pos()[1], ui.dpg.get_viewport_width(), ui.dpg.get_viewport_height()
        if window_x < x < window_x + window_w and window_y < y < window_y + window_h:
            if ctypes.windll.user32.GetForegroundWindow() == ctypes.windll.user32.FindWindowW(None, variables.WINDOWNAME):
                global left_clicked
                global right_clicked
                if str(button) == "Button.left":
                    left_clicked = pressed
                if str(button) == "Button.right":
                    right_clicked = pressed
    with Listener(on_click=on_click, on_scroll=on_scroll) as listener:
        listener.join()
threading.Thread(target=mouse_handler, daemon=True).start()

def get_speed():
    speed = ctypes.c_int()
    ctypes.windll.user32.SystemParametersInfoA(112, 0, ctypes.byref(speed), 0)
    return speed.value
variables.MOUSE_DEFAULT_SPEED = get_speed()

def set_speed(speed):
    ctypes.windll.user32.SystemParametersInfoA(113, 0, speed, 0)

def get_position():
    global mouse_slowed
    global last_window

    try:
        mouse_x, mouse_y = mouse.get_position()
        rect = win32gui.GetClientRect(variables.HWND)
        tl = win32gui.ClientToScreen(variables.HWND, (rect[0], rect[1]))
        br = win32gui.ClientToScreen(variables.HWND, (rect[2], rect[3]))
        window_x, window_y, window_width, window_height = (tl[0], tl[1], br[0] - tl[0], br[1] - tl[1])
    except:
        if last_mouse_x != None and last_mouse_y != None:
            mouse_x = last_mouse_x
            mouse_y = last_mouse_y
        else:
            mouse_x = variables.SCREEN_WIDTH // 2
            mouse_y = variables.SCREEN_HEIGHT // 2
        if last_window != (None, None, None, None):
            window_x, window_y, window_width, window_height = last_window
        else:
            window_x = settings.Get("Window", "X", variables.SCREEN_WIDTH // 4)
            window_y = settings.Get("Window", "Y", variables.SCREEN_HEIGHT // 4)
            window_width = settings.Get("Window", "Width", variables.SCREEN_WIDTH // 2)
            window_height = settings.Get("Window", "Height", variables.SCREEN_HEIGHT // 2)

    mouse_x -= window_x
    mouse_y -= window_y
    mouse_x_relative = mouse_x / window_width
    mouse_y_relative = mouse_y / window_height

    if 0 < mouse_x_relative < 1 and 0 < mouse_y_relative < 1 and mouse_slowed == False:
        mouse_slowed = True
        set_speed(round(variables.MOUSE_DEFAULT_SPEED / 2))
    elif mouse_x_relative < 0 or mouse_y_relative < 0 or mouse_x_relative> 1 or mouse_y_relative > 1:
        if mouse_slowed == True:
            mouse_slowed = False
            set_speed(variables.MOUSE_DEFAULT_SPEED)

    if last_window == (None, None, None, None):
        last_window = (window_x, window_y, window_width, window_height)

    return mouse_x, mouse_y, mouse_x_relative, mouse_y_relative, left_clicked, right_clicked, zoom