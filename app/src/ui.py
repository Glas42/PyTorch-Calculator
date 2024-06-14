import src.variables as variables
import src.settings as settings
import src.console as console

import win32gui
import pygame
import ctypes
import os

def Initialize():
    try:
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (settings.Get("Window", "X", variables.SCREEN_WIDTH // 4), settings.Get("Window", "Y", variables.SCREEN_HEIGHT // 4))
        pygame.init()
        frame = pygame.display.set_mode(size=(settings.Get("Window", "Width", variables.SCREEN_WIDTH // 2), settings.Get("Window", "Height", variables.SCREEN_HEIGHT // 2)), flags=pygame.RESIZABLE, vsync=True)
        frame.fill((0, 0, 0))
        pygame.display.set_caption(variables.WINDOWNAME)
        variables.HWND = pygame.display.get_wm_info()["window"]

        if variables.OS == "nt":
            import win32gui, win32con
            from ctypes import windll, byref, sizeof, c_int
            windll.dwmapi.DwmSetWindowAttribute(variables.HWND, 35, byref(c_int(0x000000)), sizeof(c_int))

            hicon = win32gui.LoadImage(None, f"{variables.PATH}icon.ico", win32con.IMAGE_ICON, 0, 0, win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE)
            win32gui.SendMessage(variables.HWND, win32con.WM_SETICON, win32con.ICON_SMALL, hicon)
            win32gui.SendMessage(variables.HWND, win32con.WM_SETICON, win32con.ICON_BIG, hicon)
    except:
        import traceback
        print(traceback.format_exc())

def GetMouseSpeed():
    speed = ctypes.c_int()
    ctypes.windll.user32.SystemParametersInfoA(112, 0, ctypes.byref(speed), 0)
    return speed.value

def SetMouseSpeed(speed):
    ctypes.windll.user32.SystemParametersInfoA(113, 0, speed, 0)

def GetPosition():
    rect = win32gui.GetClientRect(variables.HWND)
    tl = win32gui.ClientToScreen(variables.HWND, (rect[0], rect[1]))
    br = win32gui.ClientToScreen(variables.HWND, (rect[2], rect[3]))
    window_x, window_y, window_width, window_height = (tl[0], tl[1], br[0] - tl[0], br[1] - tl[1])
    return window_x, window_y, window_width, window_height

def Update():
    if variables.RUN == False:
        settings.Set("Window", "X", GetPosition()[0])
        settings.Set("Window", "Y", GetPosition()[1])
        settings.Set("Window", "Width", GetPosition()[2])
        settings.Set("Window", "Height", GetPosition()[3])
        if settings.Get("Console", "HideConsole", False):
            console.RestoreConsole()
            console.CloseConsole()
        SetMouseSpeed(variables.MOUSE_DEFAULT_SPEED)
    pygame.display.update()