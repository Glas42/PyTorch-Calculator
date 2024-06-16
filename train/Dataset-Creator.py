import win32gui
import ctypes
import numpy
import mss
import cv2
import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

PATH = os.path.dirname(__file__) + "\\"
DATA_FOLDER = PATH + "raw_dataset\\"

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

CLASSES = [
           "0",
           "1",
           "2",
           "3",
           "4",
           "5",
           "6",
           "7",
           "8",
           "9",
           "(",
           ")",
           "[",
           "]",
           "{",
           "}",
           "%",
           "<",
           ">",
           "<=",
           ">=",
           "+",
           "-",
           "* (multiply)",
           ": (divide)",
           "=",
           "^",
           "sqrt",
           "pi",
           "sin",
           "cos",
           "tan",
           "asin",
           "acos",
           "atan"
]

AMOUNT = [0] * len(CLASSES)

for file in os.listdir(DATA_FOLDER):
    with open(f"{DATA_FOLDER}{file}", "r") as f:
        content = str(f.read()).split("#")[0]
        if content not in CLASSES:
            print(f"{content} was not found in the list of classes")
            if input("Remove the file? (y/n) ").lower() == "y":
                f.close()
                os.remove(f"{DATA_FOLDER}{file}")
        else:
            AMOUNT[CLASSES.index(content)] += 1

print("Starting with the following dataset:")
for i in range(len(CLASSES)):
    print(f"{CLASSES[i]}: {' ' * (20-len(CLASSES[i]))} {AMOUNT[i]}")

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

def ClearFrame(list=[]):
    frame.fill((0, 0, 0))
    font = pygame.font.SysFont("calibri", 50)
    text = font.render("Last Drawing:", True, (255, 255, 255))
    frame.blit(text, (WINDOW_HEIGHT + 10, 10))
    pygame.draw.line(frame, (255, 255, 255), (WINDOW_HEIGHT, 0), (WINDOW_HEIGHT, WINDOW_HEIGHT), 3)
    pygame.draw.line(frame, (255, 255, 255), (WINDOW_HEIGHT + 15, 15 + text.get_height()), (WINDOW_WIDTH - 15, 15 + text.get_height()), 3)
    pygame.draw.line(frame, (255, 255, 255), (WINDOW_HEIGHT + 15, 15 + text.get_height()), (WINDOW_HEIGHT + 15, WINDOW_WIDTH - WINDOW_HEIGHT - 15 + text.get_height()), 3)
    pygame.draw.line(frame, (255, 255, 255), (WINDOW_WIDTH - 15, 15 + text.get_height()), (WINDOW_WIDTH - 15, WINDOW_WIDTH - WINDOW_HEIGHT - 15 + text.get_height()), 3)
    pygame.draw.line(frame, (255, 255, 255), (WINDOW_HEIGHT + 15, WINDOW_WIDTH - WINDOW_HEIGHT - 15 + text.get_height()), (WINDOW_WIDTH - 15, WINDOW_WIDTH - WINDOW_HEIGHT - 15 + text.get_height()), 3)
    if list != []:
        for points in list:
            last_point = None
            for point in points:
                point = WINDOW_HEIGHT + 30 + (point[0] * (WINDOW_WIDTH - WINDOW_HEIGHT - 60)), 30 + (point[1] * (WINDOW_WIDTH - WINDOW_HEIGHT - 60)) + text.get_height()
                if last_point == None:
                    last_point = point
                pygame.draw.line(frame, (255, 255, 255), last_point, point, 3)
                last_point = point
    # write the next class name in the middle of the screen
    font = pygame.font.SysFont("calibri", 50)
    text = font.render("Draw: " + CLASSES[AMOUNT.index(min(AMOUNT))], True, (255, 255, 255))
    frame.blit(text, (WINDOW_HEIGHT // 2 - text.get_width() // 2, 10))
ClearFrame()

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
drawlist = []

while RUN:

    current_class = CLASSES[AMOUNT.index(min(AMOUNT))]
    current_class_index = CLASSES.index(current_class)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            RUN = False
        elif event.type == pygame.VIDEORESIZE:
            WINDOW_WIDTH, WINDOW_HEIGHT = event.w, event.h
            ClearFrame(list=drawlist)

    mouse_x, mouse_y = pygame.mouse.get_pos()
    left_clicked, middle_clicked, right_clicked = pygame.mouse.get_pressed()
    if last_mouse_x is None: last_mouse_x = mouse_x
    if last_mouse_y is None: last_mouse_y = mouse_y

    if middle_clicked == True:
        list = []
        points = []
        ClearFrame(list=drawlist)

    if left_clicked == True:
        pygame.draw.line(pygame.display.get_surface(), (255, 255, 255), (last_mouse_x, last_mouse_y), (mouse_x, mouse_y), 3)
        pygame.draw.circle(pygame.display.get_surface(), (255, 255, 255), (mouse_x, mouse_y), 1)
        points.append((mouse_x, mouse_y))

    if left_clicked == False and last_left_clicked == True:
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

        temp = list
        list = []
        points = []
        for temp1 in temp:
            for point in temp1:
                if width < height:
                    x = (point[0] - x1) / height
                    y = (point[1] - y1) / height
                else:
                    x = (point[0] - x1) / width
                    y = (point[1] - y1) / width
                points.append((x, y))
            list.append(points)
            points = []

        if not os.path.exists(f"{DATA_FOLDER}"):
            os.makedirs(f"{DATA_FOLDER}")
        with open(f"{DATA_FOLDER}{len(os.listdir(f'{DATA_FOLDER}'))}.txt", "w", encoding="utf-8") as f:
            AMOUNT[current_class_index] += 1
            f.write(f"{current_class_index}#{list}")
            f.close()
        drawlist = list.copy()
        ClearFrame(list=drawlist)
        points = []
        list = []

    last_mouse_x, last_mouse_y = mouse_x, mouse_y
    last_left_clicked, last_right_clicked = left_clicked, right_clicked

    Update()

print("\nEnding with the following dataset:")
for i in range(len(CLASSES)):
    print(f"{CLASSES[i]}: {' ' * (20-len(CLASSES[i]))} {AMOUNT[i]}")

SetMouseSpeed(MOUSE_DEFAULT_SPEED)
pygame.quit()
exit()