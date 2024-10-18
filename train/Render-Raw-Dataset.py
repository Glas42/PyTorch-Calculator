import numpy
import cv2
import sys
import os

PATH = os.path.dirname(__file__).replace("\\", "/")
PATH += "/" if PATH[-1] != "/" else ""
SRC_DATA_FOLDER = PATH + "dataset/raw/"
DST_DATA_FOLDER = PATH + "dataset/final/"

RESOLUTION = 50
LINE_THICKNESS = 2

RED = "\033[91m"
GREEN = "\033[92m"
PURPLE = "\033[95m"
GRAY = "\033[90m"
NORMAL = "\033[0m"

if os.path.exists(SRC_DATA_FOLDER) == False:
    os.makedirs(SRC_DATA_FOLDER)
if os.path.exists(DST_DATA_FOLDER) == False:
    os.makedirs(DST_DATA_FOLDER)

print(f"Resolution in pixels? {GRAY}({RESOLUTION}){NORMAL}")
Resolution = None
while True:
    if Resolution == None:
        Resolution = input("-> ")
    else:
        Resolution = input(f"{RED}->{NORMAL} ")
    try:
        if Resolution == "":
            if os.name == "nt":
                sys.stdout.write("\033[1A\033[K")
                print(f"{GREEN}->{NORMAL} {RESOLUTION}")
            break
        if int(Resolution) > 0:
            RESOLUTION = int(Resolution)
            if os.name == "nt":
                sys.stdout.write("\033[1A\033[K")
                print(f"{GREEN}->{NORMAL} {RESOLUTION}")
            break
        else:
            raise
    except:
        if os.name == "nt":
            sys.stdout.write("\033[1A\033[K")
        else:
            print(RED + "Invalid input!" + NORMAL)

print(f"Line thickness in pixels? {GRAY}({LINE_THICKNESS}){NORMAL}")
LineThickness = None
while True:
    if LineThickness == None:
        LineThickness = input("-> ")
    else:
        LineThickness = input(f"{RED}->{NORMAL} ")
    try:
        if LineThickness == "":
            if os.name == "nt":
                sys.stdout.write("\033[1A\033[K")
                print(f"{GREEN}->{NORMAL} {RESOLUTION}")
            break
        if int(LineThickness) > 0:
            LINE_THICKNESS = int(LineThickness)
            if os.name == "nt":
                sys.stdout.write("\033[1A\033[K")
                print(f"{GREEN}->{NORMAL} {RESOLUTION}")
            break
        else:
            raise
    except:
        if os.name == "nt":
            sys.stdout.write("\033[1A\033[K")
        else:
            print(RED + "Invalid input!" + NORMAL)

print()
print(PURPLE + "Rendering dataset..." + NORMAL)

for File in os.listdir(DST_DATA_FOLDER):
    os.remove(f"{DST_DATA_FOLDER}{File}")

Count = 0
Total = len(os.listdir(SRC_DATA_FOLDER))
for File in os.listdir(SRC_DATA_FOLDER):
    with open(SRC_DATA_FOLDER + File, "r") as F:
        Content = F.read()
        Class, ClassIndex, CanvasContent = Content.split("###")

        ClassIndex = int(ClassIndex)
        CanvasContent = eval(CanvasContent)

        if len(CanvasContent) > 0:
            Image = numpy.zeros((RESOLUTION, RESOLUTION, 3), numpy.uint8)
            MinX = min([Point[0] if len(Point) == 2 else float("inf") for Line in CanvasContent for Point in Line])
            MinY = min([Point[1] if len(Point) == 2 else float("inf") for Line in CanvasContent for Point in Line])
            MaxX = max([Point[0] if len(Point) == 2 else float("-inf") for Line in CanvasContent for Point in Line])
            MaxY = max([Point[1] if len(Point) == 2 else float("-inf") for Line in CanvasContent for Point in Line])
            ScaleX = ((Image.shape[1] - 1 - LINE_THICKNESS) / (MaxX - MinX)) if MaxX - MinX != 0 else 1e9
            ScaleY = ((Image.shape[0] - 1 - LINE_THICKNESS)  / (MaxY - MinY)) if MaxY - MinY != 0 else 1e9
            Scale = min(ScaleX, ScaleY)
            XOffset = ((Image.shape[1] - 1 - LINE_THICKNESS) - (MaxX - MinX) * Scale) / 2
            YOffset = ((Image.shape[0] - 1 - LINE_THICKNESS) - (MaxY - MinY) * Scale) / 2
            for Line in CanvasContent:
                if len(Line[0]) == 4:
                    Line = Line[1:]
                LastPoint = None
                for Point in Line:
                    if LastPoint != None:
                        cv2.line(Image, (round((LastPoint[0] - MinX) * Scale + XOffset + LINE_THICKNESS / 2), round((LastPoint[1] - MinY) * Scale + YOffset + LINE_THICKNESS / 2)), (round((Point[0] - MinX) * Scale + XOffset + LINE_THICKNESS / 2), round((Point[1] - MinY) * Scale + YOffset + LINE_THICKNESS / 2)), (255, 255, 255), LINE_THICKNESS)
                    elif len(Line) == 1:
                        cv2.circle(Image, (round((Point[0] - MinX) * Scale + XOffset + LINE_THICKNESS / 2), round((Point[1] - MinY) * Scale + YOffset + LINE_THICKNESS / 2)), LINE_THICKNESS, (255, 255, 255), -1)
                    LastPoint = Point
            cv2.imwrite(f"{DST_DATA_FOLDER}{File.replace('.txt', '.png')}", Image)
            with open(f"{DST_DATA_FOLDER}{File}", "w") as F:
                F.write(f"{ClassIndex}")

        Count += 1
        print(f"\r{GRAY}-> Progress: {round(Count / Total * 100)}%" + NORMAL, end="", flush=True)
print(f"\r{GRAY}-> Progress: 100%" + NORMAL, end="", flush=True)

print(PURPLE + "\nDone, you can start training now!" + NORMAL)