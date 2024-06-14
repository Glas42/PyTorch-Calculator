import win32gui
import pygame
import ctypes
import mss
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

def Initialize():
    global HWND
    try:
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 4)
        pygame.init()
        frame = pygame.display.set_mode(size=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), flags=pygame.RESIZABLE, vsync=True)
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
points = []

while RUN:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            RUN = False
        elif event.type == pygame.MOUSEWHEEL:
            if event.y > 0:
                print("Mouse wheel scrolled up")
            elif event.y < 0:
                print("Mouse wheel scrolled down")

    mouse_x, mouse_y = pygame.mouse.get_pos()
    left_clicked, _, right_clicked = pygame.mouse.get_pressed()
    if last_mouse_x is None: last_mouse_x = mouse_x
    if last_mouse_y is None: last_mouse_y = mouse_y

    if left_clicked:
        pygame.draw.line(pygame.display.get_surface(), (255, 255, 255), (last_mouse_x, last_mouse_y), (mouse_x, mouse_y), 10)
        pygame.draw.circle(pygame.display.get_surface(), (255, 255, 255), (mouse_x, mouse_y), 4)
        if (mouse_x, mouse_y) != (last_mouse_x, last_mouse_y):
            points.append((mouse_x, mouse_y))

    if last_right_clicked == False and right_clicked:
        # get the coordinates of the leftmost, rightmost, topmost and bottommost point
        x1 = min(points, key=lambda p: p[0])[0]
        y1 = min(points, key=lambda p: p[1])[1]
        x2 = max(points, key=lambda p: p[0])[0]
        y2 = max(points, key=lambda p: p[1])[1]
        x1 -= 10
        y1 -= 10
        x2 += 10
        y2 += 10

        # parse the points to float numbers from 0 to 1
        width = x2 - x1
        height = y2 - y1
        if width > height:
            pass
        else:
            # normaise the points in the vertical direction, do not change the horizontal direction
            hor_norm = width / height
            points = [(p[0] - x1, (p[1] - y1) / height) for p in points]

        import cv2
        import numpy
        frame = numpy.zeros((100, 100, 3), numpy.uint8)
        for p in points:
            cv2.circle(frame, (int(p[0] * 100), int(p[1] * 100)), 5, (255, 255, 255), -1)
        cv2.imshow("image", frame)
        cv2.waitKey(1)

        if not os.path.exists(f"{PATH}raw"):
            os.makedirs(f"{PATH}raw")
        with open(f"{PATH}raw/{len(os.listdir(f'{PATH}raw'))}.txt", "w") as f:
            f.write(f"{points}")
            f.close()
        points = []

    last_mouse_x, last_mouse_y = mouse_x, mouse_y
    last_left_clicked, last_right_clicked = left_clicked, right_clicked

    Update()

SetMouseSpeed(MOUSE_DEFAULT_SPEED)
pygame.quit()
exit()