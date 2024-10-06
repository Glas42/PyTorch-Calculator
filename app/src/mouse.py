from src.crashreport import CrashReport
import src.variables as variables
import src.settings as settings
import threading
import traceback
import ctypes
import pynput
import mouse
import numpy
import time

if variables.OS == "nt":
    import win32gui

def GetMouseSpeed():
    Speed = ctypes.c_int()
    ctypes.windll.user32.SystemParametersInfoA(112, 0, ctypes.byref(Speed), 0)
    return Speed.value

def SetMouseSpeed(Speed=variables.DEFAULT_MOUSE_SPEED):
    if type(Speed) != int:
        return
    Speed = int(Speed)
    if Speed < 1:
        Speed = 1
    elif Speed > 20:
        Speed = 20
    ctypes.windll.user32.SystemParametersInfoA(113, 0, Speed, 0)

def Run():
    variables.DEFAULT_MOUSE_SPEED = GetMouseSpeed()

    def RunThread():
        try:
            LastLeftClicked = False
            LastRightClicked = False
            LastMouseX = 0
            LastMouseY = 0
            MoveStart = 0, 0
            while variables.BREAK == False:
                if win32gui.GetForegroundWindow() != variables.HWND or variables.PAGE != "Canvas":
                    time.sleep(0.1)
                    continue

                RECT = win32gui.GetClientRect(variables.HWND)
                TL = win32gui.ClientToScreen(variables.HWND, (RECT[0], RECT[1]))
                BR = win32gui.ClientToScreen(variables.HWND, (RECT[2], RECT[3]))
                WindowX, WindowY, WindowWidth, WindowHeight = TL[0], TL[1] + 40, BR[0] - TL[0], BR[1] - TL[1]
                MouseX, MouseY = mouse.get_position()

                LeftClicked = ctypes.windll.user32.GetKeyState(0x01) & 0x8000 != 0 and WindowX <= MouseX <= WindowX + WindowWidth and WindowY <= MouseY <= WindowY + WindowHeight
                RightClicked = ctypes.windll.user32.GetKeyState(0x02) & 0x8000 != 0 and WindowX <= MouseX <= WindowX + WindowWidth and WindowY <= MouseY <= WindowY + WindowHeight

                if WindowX <= MouseX <= WindowX + WindowWidth and WindowY <= MouseY <= WindowY + WindowHeight:
                    variables.HOVERING_CANVAS = True
                    if GetMouseSpeed() == variables.DEFAULT_MOUSE_SPEED:
                        SetMouseSpeed(variables.DEFAULT_MOUSE_SPEED * variables.MOUSE_SLOWDOWN)
                else:
                    variables.HOVERING_CANVAS = False
                    if GetMouseSpeed() != variables.DEFAULT_MOUSE_SPEED:
                        SetMouseSpeed(variables.DEFAULT_MOUSE_SPEED)

                if WindowX + WindowWidth - 40 <= MouseX <= WindowX + WindowWidth and WindowY - 40 <= MouseY <= WindowY and variables.TOOLBAR_HOVERED == False:
                    variables.TOOLBAR_HOVERED = True
                elif WindowX + WindowWidth - variables.TOOLBAR_WIDTH - 20 <= MouseX <= WindowX + WindowWidth and WindowY - 40 <= MouseY <= WindowY + variables.TOOLBAR_HEIGHT + 20 and variables.TOOLBAR_HOVERED == True:
                    variables.TOOLBAR_HOVERED = True
                else:
                    variables.TOOLBAR_HOVERED = False

                    if WindowX <= MouseX <= WindowX + WindowWidth and WindowY <= MouseY <= WindowY + WindowHeight:
                        with pynput.mouse.Events() as Events:
                            Event = Events.get()
                            if isinstance(Event, pynput.mouse.Events.Scroll):
                                CanvasX = (MouseX - WindowX - variables.CANVAS_POSITION[0]) / variables.CANVAS_ZOOM
                                CanvasY = (MouseY - WindowY - variables.CANVAS_POSITION[1]) / variables.CANVAS_ZOOM
                                if variables.CANVAS_ZOOM < 10000:
                                    variables.CANVAS_ZOOM = variables.CANVAS_ZOOM * 1.1 if Event.dy > 0 else variables.CANVAS_ZOOM / 1.1
                                elif Event.dy < 0:
                                    variables.CANVAS_ZOOM /= 1.1
                                variables.CANVAS_POSITION = (MouseX - WindowX - CanvasX * variables.CANVAS_ZOOM, MouseY - WindowY - CanvasY * variables.CANVAS_ZOOM)

                    if RightClicked == False:
                        MoveStart = MouseX - variables.CANVAS_POSITION[0], MouseY - variables.CANVAS_POSITION[1]
                    else:
                        variables.CANVAS_POSITION = (MouseX - MoveStart[0]), (MouseY - MoveStart[1])

                    if LeftClicked == True and (MouseX - WindowX, MouseY - WindowY) not in variables.CANVAS_TEMP:
                        variables.CANVAS_TEMP.append(((MouseX - WindowX - variables.CANVAS_POSITION[0]) * 1/variables.CANVAS_ZOOM, (MouseY - WindowY - variables.CANVAS_POSITION[1]) * 1/variables.CANVAS_ZOOM))

                    if LeftClicked == False and LastLeftClicked == True:
                        if variables.SMOOTH_LINES:
                            TEMP = []
                            for Point in variables.CANVAS_TEMP:
                                if Point not in TEMP:
                                    TEMP.append(Point)
                            variables.CANVAS_TEMP = TEMP
                            Smoothness = len(variables.CANVAS_TEMP) // 50
                            for _ in range(Smoothness):
                                TEMP = []
                                for i in range(len(variables.CANVAS_TEMP)):
                                    if i < Smoothness:
                                        XAvg = sum(P[0] for P in variables.CANVAS_TEMP[:i+Smoothness+1]) // (i+Smoothness+1)
                                        YAvg = sum(P[1] for P in variables.CANVAS_TEMP[:i+Smoothness+1]) // (i+Smoothness+1)
                                        TEMP.append((XAvg, YAvg))
                                    elif i >= len(variables.CANVAS_TEMP) - Smoothness:
                                        XAvg = sum(P[0] for P in variables.CANVAS_TEMP[i-Smoothness:]) // (len(variables.CANVAS_TEMP) - i + Smoothness)
                                        YAvg = sum(P[1] for P in variables.CANVAS_TEMP[i-Smoothness:]) // (len(variables.CANVAS_TEMP) - i + Smoothness)
                                        TEMP.append((XAvg, YAvg))
                                    else:
                                        XAvg = sum(P[0] for P in variables.CANVAS_TEMP[i-Smoothness:i+Smoothness+1]) // (2*Smoothness + 1)
                                        YAvg = sum(P[1] for P in variables.CANVAS_TEMP[i-Smoothness:i+Smoothness+1]) // (2*Smoothness + 1)
                                        TEMP.append((XAvg, YAvg))
                                variables.CANVAS_TEMP = TEMP

                        if variables.UPSCALE_LINES:
                            TEMP = []
                            for _ in range(15):
                                for i in range(len(variables.CANVAS_TEMP)-2):
                                    X1, Y1 = variables.CANVAS_TEMP[i]
                                    X2, Y2 = variables.CANVAS_TEMP[i+1]
                                    X3, Y3 = variables.CANVAS_TEMP[i+2]
                                    X = (X1*0.3 + X2*0.4 + X3*0.3)
                                    Y = (Y1*0.3 + Y2*0.4 + Y3*0.3)
                                    TEMP.append((X, Y))
                            TEMP.append(variables.CANVAS_TEMP[-1])
                            variables.CANVAS_TEMP = TEMP

                        if variables.SMOOTH_INTERPOLATION:
                            if len(variables.CANVAS_TEMP) > 1:
                                TEMP = []
                                for i in range(len(variables.CANVAS_TEMP) - 1):
                                    p0 = variables.CANVAS_TEMP[max(i - 1, 0)]
                                    p1 = variables.CANVAS_TEMP[i]
                                    p2 = variables.CANVAS_TEMP[min(i + 1, len(variables.CANVAS_TEMP) - 1)]
                                    p3 = variables.CANVAS_TEMP[min(i + 2, len(variables.CANVAS_TEMP) - 1)]
                                    for t in numpy.linspace(0, 1, 50):
                                        X = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t**2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t**3)
                                        Y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t**2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t**3)
                                        TEMP.append([X, Y])
                                variables.CANVAS_TEMP = TEMP

                        TEMP = []
                        TEMP.append((min(P[0] for P in variables.CANVAS_TEMP), min(P[1] for P in variables.CANVAS_TEMP), max(P[0] for P in variables.CANVAS_TEMP), max(P[1] for P in variables.CANVAS_TEMP)))
                        for Point in variables.CANVAS_TEMP:
                            if Point not in TEMP:
                                TEMP.append(Point)
                        variables.CANVAS_CONTENT.append(TEMP)
                        variables.CANVAS_TEMP = []

                LastMouseX, LastMouseY = MouseX, MouseY
                LastLeftClicked, LastRightClicked = LeftClicked, RightClicked
        except:
            CrashReport("Mouse - Error in function RunThread.", str(traceback.format_exc()))

    threading.Thread(target=RunThread, daemon=True).start()