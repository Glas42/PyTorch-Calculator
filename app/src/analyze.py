from src.crashreport import CrashReport
import src.variables as variables
import SimpleWindow
import itertools
import threading
import traceback
import numpy
import time
import cv2


BLUE = "\033[94m"
GRAY = "\033[90m"
GREEN = "\033[92m"
PURPLE = "\033[95m"
NORMAL = "\033[0m"

UPDATING = False


def Initialize():
    global MaxLinesToCompareToAtOnce
    global MaxClosestLinesToConsider
    global LastContent
    global EmptyFrame
    global BaseImage
    global Frame

    if variables.DEVMODE:
        SimpleWindow.Initialize(Name="PyTorch-Calculator (Dev Mode)", Size=(500, 500), Position=(variables.X + variables.WIDTH + 5, variables.Y), Resizable=False, TopMost=False, Undestroyable=False, Icon=f"{variables.PATH}app/assets/{'icon_dark' if variables.THEME == 'Dark' else 'icon_light'}.ico")

    MaxLinesToCompareToAtOnce = 5
    MaxClosestLinesToConsider = 5

    LastContent = None
    EmptyFrame = numpy.zeros((500, 500, 3), numpy.uint8)
    BaseImage = numpy.zeros((50, 50, 3), numpy.uint8)
    Frame = EmptyFrame.copy()


def Update():
    try:
        def UpdateThread():
            try:
                global UPDATING
                while UPDATING:
                    time.sleep(0.1)
                UPDATING = True
                global LastContent
                global EmptyFrame
                global Frame

                Content = (len(variables.CANVAS_CONTENT))

                if variables.PAGE == "Canvas" and LastContent != Content:
                    if variables.DEVMODE:
                        Frame = EmptyFrame.copy()
                    CANVAS_CONTENT = variables.CANVAS_CONTENT

                    Start = time.perf_counter()

                    print(PURPLE + "Analyzing content..." + NORMAL)
                    print(GRAY + f"-> Lines: {len(CANVAS_CONTENT)}" + NORMAL)
                    print(GRAY + f"-> Points: {sum([len(line) if len(line[0]) != 4 else len(line[1:]) for line in CANVAS_CONTENT])}" + NORMAL)

                    print(BLUE + "Generating combinations..." + NORMAL)
                    Combinations = [[line[1:]] for line in CANVAS_CONTENT]
                    for r in range(2, min(len(CANVAS_CONTENT) + 1, MaxLinesToCompareToAtOnce + 1)):
                        for i in range(len(CANVAS_CONTENT)):
                            ClosestLines = CANVAS_CONTENT[i:i + MaxClosestLinesToConsider]
                            for Combination in itertools.combinations(ClosestLines, r):
                                CombinedLines = []
                                for line in Combination:
                                    if len(line[0]) == 4:
                                        line = line[1:]
                                    CombinedLines.append(line)
                                Combinations.append(CombinedLines)
                    print(GRAY + f"-> Possible combinations: {len(Combinations)}" + NORMAL)

                    print(BLUE + "Interpreting combinations..." + NORMAL)

                    for Combination in Combinations:
                        Image = BaseImage.copy()
                        LastLen = 0
                        MinX = min([Point[0] for Line in Combination for Point in Line])
                        MinY = min([Point[1] for Line in Combination for Point in Line])
                        MaxX = max([Point[0] for Line in Combination for Point in Line])
                        MaxY = max([Point[1] for Line in Combination for Point in Line])
                        ScaleX = ((Image.shape[1] - 1) / (MaxX - MinX)) if MaxX - MinX != 0 else 1e9
                        ScaleY = ((Image.shape[0] - 1)  / (MaxY - MinY)) if MaxY - MinY != 0 else 1e9
                        Scale = min(ScaleX, ScaleY)
                        XOffset = ((Image.shape[1] - 1) - (MaxX - MinX) * Scale) / 2
                        YOffset = ((Image.shape[0] - 1) - (MaxY - MinY) * Scale) / 2
                        for Line in Combination:
                            LastPoint = None
                            for Point in Line:
                                if LastPoint != None:
                                    cv2.line(Image, (round((LastPoint[0] - MinX) * Scale + XOffset), round((LastPoint[1] - MinY) * Scale + YOffset)), (round((Point[0] - MinX) * Scale + XOffset), round((Point[1] - MinY) * Scale + YOffset)), (255, 255, 255), 1)
                                elif len(Line) == 1:
                                    cv2.line(Image, (round((Point[0] - MinX) * Scale + XOffset), round((Point[1] - MinY) * Scale + YOffset)), (round((Point[0] - MinX) * Scale + XOffset), round((Point[1] - MinY) * Scale + YOffset)), (255, 255, 255), 1)
                                LastPoint = Point
                        if len(Combination) > LastLen:
                            LastLen = len(Combination)
                            EmptyFrame = cv2.resize(Image, (500, 500))
                            Frame = EmptyFrame.copy()

                    print("NOT IMPLEMENTED: Check all combinations using a classification model.")

                    print(PURPLE + f"Analyzing completed!" + NORMAL)
                    print(GRAY + f"-> {round((time.perf_counter() - Start), 2)}s" + NORMAL)
                    print()

                    LastContent = Content

                UPDATING = False
            except:
                CrashReport("Analyze - Error in function Update.", str(traceback.format_exc()))
        threading.Thread(target=UpdateThread, daemon=True).start()
        if variables.DEVMODE:
            SimpleWindow.Show("PyTorch-Calculator (Dev Mode)", Frame)
    except:
        CrashReport("Analyze - Error in function Update.", str(traceback.format_exc()))