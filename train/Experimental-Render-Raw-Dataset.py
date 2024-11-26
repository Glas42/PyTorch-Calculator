import random
import numpy
import math
import cv2
import sys
import os

PATH = os.path.dirname(__file__).replace("\\", "/")
PATH += "/" if PATH[-1] != "/" else ""
SRC_DATA_FOLDER = PATH + "dataset/raw/"
DST_DATA_FOLDER = PATH + "dataset/final/"

RESOLUTION = 500

RED = "\033[91m"
GREEN = "\033[92m"
PURPLE = "\033[95m"
GRAY = "\033[90m"
NORMAL = "\033[0m"

if os.path.exists(SRC_DATA_FOLDER) == False:
    os.makedirs(SRC_DATA_FOLDER)
if os.path.exists(DST_DATA_FOLDER) == False:
    os.makedirs(DST_DATA_FOLDER)

print(f"Resolution in points per object? {GRAY}({RESOLUTION}){NORMAL}")
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
        if int(Resolution) > 10:
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

print()
print(PURPLE + "Converting dataset..." + NORMAL)

for File in os.listdir(DST_DATA_FOLDER):
    if File.endswith(".md") == False:
        os.remove(f"{DST_DATA_FOLDER}{File}")

Count = 0
Total = len(os.listdir(SRC_DATA_FOLDER))
for File in os.listdir(SRC_DATA_FOLDER):
    if File.endswith(".txt"):
        with open(SRC_DATA_FOLDER + File, "r") as F:
            Content = F.read()
            Class, ClassIndex, CanvasContent = Content.split("###")

            ClassIndex = int(ClassIndex)
            CanvasContent = eval(CanvasContent)

            if len(CanvasContent) > 0:

                MinX = min([Point[0] if len(Point) == 2 else float("inf") for Line in CanvasContent for Point in Line])
                MinY = min([Point[1] if len(Point) == 2 else float("inf") for Line in CanvasContent for Point in Line])
                MaxX = max([Point[0] if len(Point) == 2 else float("-inf") for Line in CanvasContent for Point in Line])
                MaxY = max([Point[1] if len(Point) == 2 else float("-inf") for Line in CanvasContent for Point in Line])
                NewCanvasContent = []
                for Line in CanvasContent:
                    NewLine = []
                    if len(Line[0]) == 4:
                        Line = Line[1:]
                    for Point in Line:
                        X, Y = Point
                        X -= MinX
                        Y -= MinY
                        X = X / (MaxX - MinX)
                        Y = Y / (MaxY - MinY)
                        NewLine.append((X, Y))
                    NewCanvasContent.append(NewLine)
                CanvasContent = NewCanvasContent


                if sum(len(Line) for Line in CanvasContent) > RESOLUTION:
                    while sum(len(Line) for Line in CanvasContent) > RESOLUTION:
                        Distances = []
                        for i, Line in enumerate(CanvasContent):
                            for j, Point in enumerate(Line):
                                if 0 < j < len(Line) - 2:
                                    DistanceToPrevious = math.sqrt((Line[j - 1][0] - Point[0]) ** 2 + (Line[j - 1][1] - Point[1]) ** 2)
                                    DistanceToNext = math.sqrt((Line[j + 1][0] - Point[0]) ** 2 + (Line[j + 1][1] - Point[1]) ** 2)
                                    Distances.append((DistanceToPrevious + DistanceToNext, i, j))
                        _, i, j = min(Distances, key=lambda x: x[0])
                        del CanvasContent[i][j]

                elif sum(len(Line) for Line in CanvasContent) < RESOLUTION:
                    while sum(len(Line) for Line in CanvasContent) < RESOLUTION:
                        Distances = []
                        for i, Line in enumerate(CanvasContent):
                            for j, Point in enumerate(Line):
                                if 0 < j < len(Line) - 2:
                                    DistanceToPrevious = math.sqrt((Line[j - 1][0] - Point[0]) ** 2 + (Line[j - 1][1] - Point[1]) ** 2)
                                    DistanceToNext = math.sqrt((Line[j + 1][0] - Point[0]) ** 2 + (Line[j + 1][1] - Point[1]) ** 2)
                                    Distances.append((DistanceToPrevious + DistanceToNext, i, j))
                        _, i, j = max(Distances, key=lambda x: x[0])
                        CanvasContent[i].insert(j, ((CanvasContent[i][j - 1][0] + CanvasContent[i][j][0]) / 2, (CanvasContent[i][j - 1][1] + CanvasContent[i][j][1]) / 2))

                NewCanvasContent = []
                for Line in CanvasContent:
                    for Point in Line:
                        X, Y = Point
                        NewCanvasContent.append((X, Y))
                CanvasContent = NewCanvasContent

                CanvasContent.sort(key=lambda x: x[1])
                SortedCanvasContent = []
                while len(CanvasContent) > 0:
                    LowestY = min(CanvasContent, key=lambda x: x[1])
                    SortedCanvasContent.extend(sorted([p for p in CanvasContent if p[1] == LowestY[1]], key=lambda x: x[0]))
                    CanvasContent = [p for p in CanvasContent if p[1] > LowestY[1]]
                CanvasContent = SortedCanvasContent

                with open(f"{DST_DATA_FOLDER}{File}", "w") as F:
                    F.write(f"{Class}###{CanvasContent}")

            Count += 1
            print(f"\r{GRAY}-> Progress: {round(Count / Total * 100)}%" + NORMAL, end="", flush=True)
    else:
        if File.endswith(".md") == False:
            os.remove(SRC_DATA_FOLDER + File)
print(f"\r{GRAY}-> Progress: 100%" + NORMAL, end="", flush=True)

print(PURPLE + "\nDone, you can start training now!" + NORMAL)