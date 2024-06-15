import win32gui
import pygame
import ctypes
import numpy
import mss
import cv2
import os

PATH = os.path.dirname(__file__) + "\\"

OS = os.name

RUN = True
WINDOWNAME = "Generate-Training-Data"
MOUSE_DEFAULT_SPEED = 10

sct = mss.mss()
SCRENN_X = sct.monitors[1]["left"]
SCRENN_Y = sct.monitors[1]["top"]
SCREEN_WIDTH = sct.monitors[1]["width"]
SCREEN_HEIGHT = sct.monitors[1]["height"]

WINDOW_WIDTH = SCREEN_WIDTH // 2
WINDOW_HEIGHT = SCREEN_HEIGHT // 2

def Initialize():
    global HWND
    global frame
    try:
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 4)
        pygame.init()
        frame = pygame.display.set_mode(size=(WINDOW_WIDTH, WINDOW_HEIGHT), flags=pygame.RESIZABLE, vsync=True)
        frame.fill((0, 0, 0))
        pygame.display.set_caption(WINDOWNAME)
        HWND = pygame.display.get_wm_info()["window"]

        if OS == "nt":
            import win32gui, win32con
            from ctypes import windll, byref, sizeof, c_int
            windll.dwmapi.DwmSetWindowAttribute(HWND, 35, byref(c_int(0x000000)), sizeof(c_int))

            hicon = win32gui.LoadImage(None, f"{PATH}icon.ico", win32con.IMAGE_ICON, 0, 0, win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE)
            win32gui.SendMessage(HWND, win32con.WM_SETICON, win32con.ICON_SMALL, hicon)
            win32gui.SendMessage(HWND, win32con.WM_SETICON, win32con.ICON_BIG, hicon)
    except:
        import traceback
        print(traceback.format_exc())
Initialize()

def GetMouseSpeed():
    speed = ctypes.c_int()
    ctypes.windll.user32.SystemParametersInfoA(112, 0, ctypes.byref(speed), 0)
    return speed.value

def SetMouseSpeed(speed):
    ctypes.windll.user32.SystemParametersInfoA(113, 0, speed, 0)

def GetPosition():
    rect = win32gui.GetClientRect(HWND)
    tl = win32gui.ClientToScreen(HWND, (rect[0], rect[1]))
    br = win32gui.ClientToScreen(HWND, (rect[2], rect[3]))
    window_x, window_y, window_width, window_height = (tl[0], tl[1], br[0] - tl[0], br[1] - tl[1])
    return window_x, window_y, window_width, window_height

def Update():
    if RUN == False:
        SetMouseSpeed(MOUSE_DEFAULT_SPEED)
    pygame.display.update()

MOUSE_DEFAULT_SPEED = GetMouseSpeed()

last_left_clicked = False
last_right_clicked = False
last_mouse_x = None
last_mouse_y = None
list = []
points = []

while RUN:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            RUN = False
        elif event.type == pygame.VIDEORESIZE:
            WINDOW_WIDTH, WINDOW_HEIGHT = event.w, event.h
            frame = pygame.display.set_mode(size=(WINDOW_WIDTH, WINDOW_HEIGHT), flags=pygame.RESIZABLE, vsync=True)

    pygame.draw.line(frame, (255, 255, 255), (WINDOW_HEIGHT, 0), (WINDOW_HEIGHT, WINDOW_HEIGHT), 3)

    mouse_x, mouse_y = pygame.mouse.get_pos()
    left_clicked, _, right_clicked = pygame.mouse.get_pressed()
    if last_mouse_x is None: last_mouse_x = mouse_x
    if last_mouse_y is None: last_mouse_y = mouse_y

    if left_clicked == True:
        pygame.draw.line(pygame.display.get_surface(), (255, 255, 255), (last_mouse_x, last_mouse_y), (mouse_x, mouse_y), 10)
        pygame.draw.circle(pygame.display.get_surface(), (255, 255, 255), (mouse_x, mouse_y), 4)
        points.append((mouse_x, mouse_y))

    if left_clicked == False and last_left_clicked == True:
        # remove points that are muliple times in the list
        temp = []
        for point in points:
            if point not in temp:
                temp.append(point)
        points = temp
        list.append(points)
        points = []

    if last_right_clicked == False and right_clicked == True:
        if len(list) == 0:
            continue
        for points in list:
            if len(points) == 0:
                list.remove(points)

        x1 = float('inf')
        y1 = float('inf')
        x2 = 0
        y2 = 0
        for points in list:
            x1 = min(points, key=lambda p: p[0])[0] if min(points, key=lambda p: p[0])[0] < x1 else x1
            y1 = min(points, key=lambda p: p[1])[1] if min(points, key=lambda p: p[1])[1] < y1 else y1
            x2 = max(points, key=lambda p: p[0])[0] if max(points, key=lambda p: p[0])[0] > x2 else x2
            y2 = max(points, key=lambda p: p[1])[1] if max(points, key=lambda p: p[1])[1] > y2 else y2

        width = x2 - x1
        height = y2 - y1
        if width == 0:
            width = 1
        if height == 0:
            height = 1

        temp = list
        list = []
        points = []
        for temp1 in temp:
            for point in temp1:
                x, y = point
                if height > width:
                    x = height // 2 + x - (x2 - x1) // 2
                else:
                    y = width // 2 + y - (y2 - y1) // 2
                points.append((x, y))
            list.append(points)
            points = []

        frame_1 = numpy.zeros((300, 300, 3), numpy.uint8)
        for points in list:
            normalized_points = []
            for point in points:
                if width < height:
                    x = (point[0] - x1) / height
                    y = (point[1] - y1) / height
                else:
                    x = (point[0] - x1) / width
                    y = (point[1] - y1) / width
                normalized_points.append((x, y))
            points = normalized_points

            last_point = None
            for point in points:
                if last_point == None:
                    last_point = point
                cv2.line(frame_1, (round(last_point[0] * 299), round(last_point[1] * 299)), (round(point[0] * 299), round(point[1] * 299)), (255, 255, 255), 1)
                last_point = point
            cv2.imshow("image", frame_1)
            cv2.waitKey(1)

        if not os.path.exists(f"{PATH}raw"):
            os.makedirs(f"{PATH}raw")
        with open(f"{PATH}raw/{len(os.listdir(f'{PATH}raw'))}.txt", "w") as f:
            f.write(f"{points}")
            f.close()
        points = []
        list = []
        frame.fill((0, 0, 0))

    last_mouse_x, last_mouse_y = mouse_x, mouse_y
    last_left_clicked, last_right_clicked = left_clicked, right_clicked

    Update()

SetMouseSpeed(MOUSE_DEFAULT_SPEED)
pygame.quit()
exit()