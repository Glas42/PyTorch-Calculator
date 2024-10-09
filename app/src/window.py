from ctypes import windll, byref, sizeof, c_int
import win32gui, win32con
import OpenGL.GL as gl
import numpy
import glfw
import cv2
import os


WINDOWS = {}


def Initialize(Name="", Size=(None, None), Position=(None, None), TitleBarColor=(0, 0, 0), Resizable=True, TopMost=False, Undestroyable=False, Icon=""):
    WINDOWS[Name] = {"Size": Size, "Position": Position, "TitleBarColor": TitleBarColor, "Resizable": Resizable, "TopMost": TopMost, "Undestroyable": Undestroyable, "Icon": Icon, "Created": False, "Window": None, "Texture": None}


def CreateWindow(Name=""):
    Size = WINDOWS[Name]["Size"]
    Position = WINDOWS[Name]["Position"]
    TitleBarColor = WINDOWS[Name]["TitleBarColor"]
    Resizable = WINDOWS[Name]["Resizable"]
    TopMost = WINDOWS[Name]["TopMost"]
    Icon = WINDOWS[Name]["Icon"]

    glfw.init()

    if Size[0] == None:
        Size = 150, Size[1]
    if Size[1] == None:
        Size = Size[0], 50

    if Position[0] == None:
        Position = 0, Position[1]
    if Position[1] == None:
        Position = Position[0], 0

    Window = glfw.create_window(Size[0], Size[1], Name, None, None)
    glfw.make_context_current(Window)

    if Resizable == False:
        glfw.set_window_attrib(Window, glfw.RESIZABLE, glfw.FALSE)

    if TopMost:
        glfw.set_window_attrib(Window, glfw.FLOATING, glfw.TRUE)

    glfw.set_window_pos(Window, Position[0], Position[1])

    Frame = numpy.zeros((Size[1], Size[0], 3), dtype=numpy.uint8)
    Frame[:] = TitleBarColor
    WindowHeight, WindowWidth, Channels = Frame.shape

    HWND = win32gui.FindWindow(None, Name)
    windll.dwmapi.DwmSetWindowAttribute(HWND, 35, byref(c_int((TitleBarColor[0] << 16) | (TitleBarColor[1] << 8) | TitleBarColor[2])), sizeof(c_int))
    Icon = Icon.replace("\\", "/")
    if os.path.exists(Icon) and Icon.endswith(".ico"):
        Icon = win32gui.LoadImage(None, Icon, win32con.IMAGE_ICON, 0, 0, win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE)
        win32gui.SendMessage(HWND, win32con.WM_SETICON, win32con.ICON_SMALL, Icon)
        win32gui.SendMessage(HWND, win32con.WM_SETICON, win32con.ICON_BIG, Icon)

    Texture = gl.glGenTextures(1)
    gl.glBindTexture(gl.GL_TEXTURE_2D, Texture)

    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, WindowWidth, WindowHeight, 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, Frame)

    gl.glEnable(gl.GL_TEXTURE_2D)

    WINDOWS[Name]["Created"] = True
    WINDOWS[Name]["Window"] = Window
    WINDOWS[Name]["Texture"] = Texture


def GetWindowSize(Name=""):
    if WINDOWS[Name]["Created"] == True:
        HWND = win32gui.FindWindow(None, Name)
        RECT = win32gui.GetClientRect(HWND)
        TopLeft = win32gui.ClientToScreen(HWND, (RECT[0], RECT[1]))
        BottomRight = win32gui.ClientToScreen(HWND, (RECT[2], RECT[3]))
        return BottomRight[0] - TopLeft[0], BottomRight[1] - TopLeft[1]
    return WINDOWS[Name]["Size"]


def SetWindowSize(Name="", Size=(None, None)):
    if WINDOWS[Name]["Size"] != Size and WINDOWS[Name]["Created"] == True:
        if Size[0] == None:
            Size = WINDOWS[Name]["Size"][0], Size[1]
        if Size[1] == None:
            Size = Size[0], WINDOWS[Name]["Size"][1]
        WINDOWS[Name]["Size"] = Size
        glfw.set_window_size(WINDOWS[Name]["Window"], Size[0], Size[1])


def GetWindowPosition(Name=""):
    if WINDOWS[Name]["Created"] == True:
        HWND = win32gui.FindWindow(None, Name)
        RECT = win32gui.GetClientRect(HWND)
        TopLeft = win32gui.ClientToScreen(HWND, (RECT[0], RECT[1]))
        return TopLeft[0], TopLeft[1]
    return 0, 0


def SetWindowPosition(Name="", Position=(None, None)):
    if WINDOWS[Name]["Position"] != Position and WINDOWS[Name]["Created"] == True:
        if Position[0] == None:
            Position = WINDOWS[Name]["Position"][0], Position[1]
        if Position[1] == None:
            Position = Position[0], WINDOWS[Name]["Position"][1]
        WINDOWS[Name]["Position"] = Position
        glfw.set_window_pos(WINDOWS[Name]["Window"], Position[0], Position[1])


def SetTitleBarColor(Name="", TitleBarColor=(0, 0, 0)):
    if WINDOWS[Name]["TitleBarColor"] != TitleBarColor and WINDOWS[Name]["Created"] == True:
        WINDOWS[Name]["TitleBarColor"] = TitleBarColor
        HWND = win32gui.FindWindow(None, Name)
        windll.dwmapi.DwmSetWindowAttribute(HWND, 35, byref(c_int((TitleBarColor[0] << 16) | (TitleBarColor[1] << 8) | TitleBarColor[2])), sizeof(c_int))


def SetResizable(Name="", Resizable=True):
    if WINDOWS[Name]["Resizable"] != Resizable:
        WINDOWS[Name]["Resizable"] = Resizable
        Close(Name)
        Initialize(Name=Name, Size=WINDOWS[Name]["Size"], Position=WINDOWS[Name]["Position"], TitleBarColor=WINDOWS[Name]["TitleBarColor"], Resizable=WINDOWS[Name]["Resizable"], TopMost=WINDOWS[Name]["TopMost"], Icon=WINDOWS[Name]["Icon"])


def SetTopMost(Name="", TopMost=True):
    if WINDOWS[Name]["TopMost"] != TopMost:
        WINDOWS[Name]["TopMost"] = TopMost
        Close(Name)
        Initialize(Name=Name, Size=WINDOWS[Name]["Size"], Position=WINDOWS[Name]["Position"], TitleBarColor=WINDOWS[Name]["TitleBarColor"], Resizable=WINDOWS[Name]["Resizable"], TopMost=WINDOWS[Name]["TopMost"], Icon=WINDOWS[Name]["Icon"])


def SetIcon(Name="", Icon=""):
    if WINDOWS[Name]["Icon"] != Icon and WINDOWS[Name]["Created"] == True:
        WINDOWS[Name]["Icon"] = Icon
        HWND = win32gui.FindWindow(None, Name)
        Icon = Icon.replace("\\", "/")
        if os.path.exists(Icon) and Icon.endswith(".ico"):
            Icon = win32gui.LoadImage(None, Icon, win32con.IMAGE_ICON, 0, 0, win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE)
            win32gui.SendMessage(HWND, win32con.WM_SETICON, win32con.ICON_SMALL, Icon)
            win32gui.SendMessage(HWND, win32con.WM_SETICON, win32con.ICON_BIG, Icon)


def GetWindowStatus(Name=""):
    HWND = win32gui.FindWindow(None, Name)
    return {"Open": WINDOWS[Name]["Created"], "HWND": HWND, "Foreground": win32gui.GetForegroundWindow() == HWND, "Iconic": int(win32gui.IsIconic(HWND)) == 0}


def Show(Name="", Frame=None):
    if WINDOWS[Name]["Created"] == False:
        CreateWindow(Name=Name)
    elif WINDOWS[Name]["Created"] == None:
        return
    if glfw.window_should_close(WINDOWS[Name]["Window"]):
        if WINDOWS[Name]["Created"] == True:
            Close(Name)
        if WINDOWS[Name]["Undestroyable"] == True:
            Initialize(Name=Name, Size=WINDOWS[Name]["Size"], Position=WINDOWS[Name]["Position"], TitleBarColor=WINDOWS[Name]["TitleBarColor"], Resizable=WINDOWS[Name]["Resizable"], TopMost=WINDOWS[Name]["TopMost"], Icon=WINDOWS[Name]["Icon"])
        else:
            WINDOWS[Name]["Created"] = None
            return

    if Frame is not None:
        Frame = cv2.flip(Frame, 0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, WINDOWS[Name]["Texture"])
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, Frame.shape[1], Frame.shape[0], 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, Frame)

    gl.glViewport(0, 0, WINDOWS[Name]["Size"][0], WINDOWS[Name]["Size"][1])
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    gl.glBindTexture(gl.GL_TEXTURE_2D, WINDOWS[Name]["Texture"])

    gl.glBegin(gl.GL_QUADS)
    gl.glTexCoord2f(0, 0)
    gl.glVertex2f(-1, -1)
    gl.glTexCoord2f(1, 0)
    gl.glVertex2f(1, -1)
    gl.glTexCoord2f(1, 1)
    gl.glVertex2f(1, 1)
    gl.glTexCoord2f(0, 1)
    gl.glVertex2f(-1, 1)
    gl.glEnd()

    glfw.swap_buffers(WINDOWS[Name]["Window"])
    glfw.poll_events()


def Close(Name=""):
    gl.glDeleteTextures([WINDOWS[Name]["Texture"]])
    glfw.terminate()
    WINDOWS[Name]["Created"] = False