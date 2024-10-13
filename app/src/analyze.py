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
    global LastContent
    global EmptyFrame
    global Frame

    if variables.DEVMODE:
        SimpleWindow.Initialize(Name="PyTorch-Calculator (Dev Mode)", Size=(500, 500), Position=(variables.X + variables.WIDTH + 5, variables.Y), Resizable=False, TopMost=False, Undestroyable=False, Icon=f"{variables.PATH}app/assets/{'icon_dark' if variables.THEME == 'Dark' else 'icon_light'}.ico")

    LastContent = None
    EmptyFrame = numpy.zeros((500, 500, 3), numpy.uint8)
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
                global Frame

                Content = (len(variables.CANVAS_CONTENT))

                if variables.PAGE == "Canvas" and LastContent != Content:
                    if variables.DEVMODE:
                        Frame = EmptyFrame.copy()
                    CANVAS_CONTENT = variables.CANVAS_CONTENT

                    print(PURPLE + "Analyzing content..." + NORMAL)
                    print(GRAY + f"-> Lines: {len(CANVAS_CONTENT)}" + NORMAL)
                    print(GRAY + f"-> Points: {sum([len(line) if len(line[0]) != 4 else len(line[1:]) for line in CANVAS_CONTENT])}" + NORMAL)

                    print(BLUE + "Generating combinations..." + NORMAL)
                    Combinations = [line[1:] for line in CANVAS_CONTENT]
                    for r in range(2, len(CANVAS_CONTENT) + 1):
                        for Combination in itertools.combinations(CANVAS_CONTENT, r):
                            CombinedLines = []
                            for line in Combination:
                                if len(line[0]) == 4:
                                    line = line[1:]
                                CombinedLines.append(line)
                            Combinations.append(CombinedLines)
                    print("NOT IMPLEMENTED: Optimize combination search by only combining items which overlap + maybe 5 closest other lines.")
                    print(GRAY + f"-> Possible combinations: {len(Combinations)}" + NORMAL)

                    print(BLUE + "Interpreting combinations..." + NORMAL)

                    print("NOT IMPLEMENTED: Render and check all combinations using a classification model.")

                    print(PURPLE + "Done!\n" + NORMAL)

                    LastContent = Content

                UPDATING = False
            except:
                CrashReport("Analyze - Error in function Update.", str(traceback.format_exc()))
        threading.Thread(target=UpdateThread, daemon=True).start()
        if variables.DEVMODE:
            SimpleWindow.Show("PyTorch-Calculator (Dev Mode)", Frame)
    except:
        CrashReport("Analyze - Error in function Update.", str(traceback.format_exc()))