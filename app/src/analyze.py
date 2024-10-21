from src.crashreport import CrashReport
import src.uicomponents as uicomponents
import src.variables as variables
import src.pytorch as pytorch
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
    global Rules
    global MaxLinesToCompareToAtOnce
    global MaxClosestLinesToConsider
    global LineThickness
    global LastContent
    global EmptyFrame
    global BaseImage
    global Frame
    global CleanFrame

    if variables.DEVMODE:
        SimpleWindow.Initialize(Name="PyTorch-Calculator (Dev Mode)", Size=(400, 400), Position=(variables.X + variables.WIDTH + 5, variables.Y + 430 + 5), Resizable=False, TopMost=False, Undestroyable=False, Icon=f"{variables.PATH}app/assets/{'icon_dark' if variables.THEME == 'Dark' else 'icon_light'}.ico")

    SimpleWindow.Initialize(Name="PyTorch-Calculator Detection", Size=(400, 400), Position=(variables.X + variables.WIDTH + 5, variables.Y), Resizable=False, TopMost=False, Undestroyable=False, Icon=f"{variables.PATH}app/assets/{'icon_dark' if variables.THEME == 'Dark' else 'icon_light'}.ico")

    pytorch.Initialize(Owner="Glas42", Model="PyTorch-Calculator")
    pytorch.Load("PyTorch-Calculator")


    Rules = [{
        "IfClass": "-",
        "PartOfClass": "+",
        "ThenClass": "None"
    },
    {
        "IfClass": "-",
        "PartOfClass": "=",
        "ThenClass": "None"
    },
    {
        "IfClass": "(",
        "PartOfClass": "+",
        "ThenClass": "None"
    },
    {
        "IfClass": ")",
        "PartOfClass": "+",
        "ThenClass": "None"
    },
    {
        "IfClass": "-",
        "PartOfClass": "/",
        "ThenClass": "None"
    },
    {
        "IfClass": "(",
        "PartOfClass": "4",
        "ThenClass": "None"
    },
    {
        "IfClass": ")",
        "PartOfClass": "4",
        "ThenClass": "None"
    },
    {
        "IfClass": "7",
        "PartOfClass": "*",
        "ThenClass": "None"
    },
    {
        "IfClass": "-",
        "PartOfClass": "5",
        "ThenClass": "None"
    }]

    MaxLinesToCompareToAtOnce = 3  # Set to 0 or less to compare to all at once
    MaxClosestLinesToConsider = 3  # Will be limited to MaxLinesToCompareToAtOnce when greater than MaxLinesToCompareToAtOnce except MaxLinesToCompareToAtOnce is 0 or less
    LineThickness = 2


    LastContent = None
    EmptyFrame = numpy.zeros((400, 400, 3), numpy.uint8)
    BaseImage = numpy.zeros((50, 50, 3), numpy.uint8)
    Frame = EmptyFrame.copy()
    CleanFrame = EmptyFrame.copy()


def ClassifyImage(Image):
    if pytorch.TorchAvailable == False: return None, 0
    while pytorch.Loaded("PyTorch-Calculator") == False and pytorch.TorchAvailable == True: time.sleep(0.1)
    Image = numpy.array(Image, dtype=numpy.float32)
    Image = cv2.cvtColor(Image, cv2.COLOR_RGB2GRAY)
    Image = cv2.resize(Image, (pytorch.MODELS["PyTorch-Calculator"]["IMG_WIDTH"], pytorch.MODELS["PyTorch-Calculator"]["IMG_HEIGHT"]))
    Image = Image / 255.0
    Image = pytorch.transforms.ToTensor()(Image).unsqueeze(0).to(pytorch.MODELS["PyTorch-Calculator"]["Device"])
    with pytorch.torch.no_grad():
        Output = numpy.array(pytorch.MODELS["PyTorch-Calculator"]["Model"](Image)[0].tolist())
    Confidence = max(Output)
    Output = numpy.argmax(Output)
    return pytorch.MODELS["PyTorch-Calculator"]["CLASS_LIST"][Output] if Confidence > 0.8 else "None", Confidence


def Update():
    try:
        def UpdateThread():
            try:
                global UPDATING
                while UPDATING:
                    time.sleep(0.01)
                UPDATING = True
                global LastContent
                global EmptyFrame
                global BaseImage
                global Frame
                global CleanFrame

                Content = (len(variables.CANVAS_CONTENT))

                if variables.PAGE == "Canvas" and LastContent != Content:
                    if variables.DEVMODE:
                        Frame = EmptyFrame.copy()
                    CANVAS_CONTENT = variables.CANVAS_CONTENT
                    CleanContent = []

                    Start = time.perf_counter()

                    if pytorch.Loaded("PyTorch-Calculator") == True and pytorch.TorchAvailable == True:
                        if pytorch.MODELS["PyTorch-Calculator"]["IMG_WIDTH"] != BaseImage.shape[1] or pytorch.MODELS["PyTorch-Calculator"]["IMG_HEIGHT"] != BaseImage.shape[0]:
                            BaseImage = numpy.zeros((pytorch.MODELS["PyTorch-Calculator"]["IMG_WIDTH"], pytorch.MODELS["PyTorch-Calculator"]["IMG_HEIGHT"], 3), numpy.uint8)

                    print(PURPLE + "Analyzing content..." + NORMAL)
                    print(GRAY + f"-> Lines: {len(CANVAS_CONTENT)}" + NORMAL)
                    print(GRAY + f"-> Points: {sum([len(Line) if len(Line[0]) != 4 else len(Line[1:]) for Line in CANVAS_CONTENT])}" + NORMAL)

                    print(BLUE + "Generating combinations..." + NORMAL)
                    Combinations = [[Line[1:]] for Line in CANVAS_CONTENT]
                    for r in range(2, min(len(CANVAS_CONTENT) + 1, float("inf") if MaxLinesToCompareToAtOnce < 1 else (MaxLinesToCompareToAtOnce + 1))):
                        for i in range(len(CANVAS_CONTENT)):
                            if MaxClosestLinesToConsider > 0:
                                MinX, MinY, MaxX, MaxY = CANVAS_CONTENT[i][0]
                                X = (MinX + MaxX) / 2
                                Y = (MinY + MaxY) / 2
                                Distances = [numpy.sqrt((Line[0][0] - X) ** 2 + (Line[0][1] - Y) ** 2) for Line in CANVAS_CONTENT]
                                OtherLines = [CANVAS_CONTENT[j] for j in numpy.argsort(Distances)[:MaxClosestLinesToConsider]]
                            else:
                                OtherLines = CANVAS_CONTENT
                            for Combination in itertools.combinations(OtherLines, r):
                                CombinedLines = []
                                for Line in Combination:
                                    if len(Line[0]) == 4:
                                        Line = Line[1:]
                                    CombinedLines.append(Line)
                                CombinedLines.sort(key=lambda Line: min([Point[0] for Point in Line]))
                                if CombinedLines not in Combinations:
                                    Combinations.append(CombinedLines)
                    print(GRAY + f"-> Possible combinations: {len(Combinations)}" + NORMAL)

                    print(BLUE + "Interpreting combinations..." + NORMAL)

                    Images = []
                    Coordinates = []

                    for Combination in Combinations:
                        Image = BaseImage.copy()
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
                                    cv2.line(Image, (round((LastPoint[0] - MinX) * Scale + XOffset), round((LastPoint[1] - MinY) * Scale + YOffset)), (round((Point[0] - MinX) * Scale + XOffset), round((Point[1] - MinY) * Scale + YOffset)), (255, 255, 255), LineThickness)
                                elif len(Line) == 1:
                                    cv2.line(Image, (round((Point[0] - MinX) * Scale + XOffset), round((Point[1] - MinY) * Scale + YOffset)), (round((Point[0] - MinX) * Scale + XOffset), round((Point[1] - MinY) * Scale + YOffset)), (255, 255, 255), LineThickness)
                                LastPoint = Point
                        Images.append(Image)
                        Coordinates.append((MinX, MinY, MaxX, MaxY, Combinations.index(Combination)))

                    NumRows = int(numpy.ceil(numpy.sqrt(len(Images))))
                    if NumRows != 0:
                        NumCols = int(numpy.ceil(len(Images) / NumRows))

                        GridWidth = NumCols * Images[0].shape[1]
                        GridHeight = NumRows * Images[0].shape[0]
                        GridImage = numpy.zeros((GridHeight, GridWidth, 3), numpy.uint8)

                        for i, Image in enumerate(Images):
                            MinX, MinY, MaxX, MaxY, Index = Coordinates[i]
                            Class, Confidence = ClassifyImage(Image)
                            if Class != "None":
                                CleanContent.append((MinX, MinY, MaxX, MaxY, Index, Class, Confidence))

                            Row = i // NumCols
                            Col = i % NumCols
                            X = Col * Image.shape[1]
                            Y = Row * Image.shape[0]
                            Text, Fontscale, Thickness, Width, Height = uicomponents.GetTextSize(f"{Class}", Image.shape[1] - 4, 10)
                            cv2.rectangle(Image, (0, 0), (Width + 2, Height + 2), (0, 0, 0), - 1)
                            cv2.rectangle(Image, (0, 0), (Width + 2, Height + 2), (127, 127, 127), 1)
                            cv2.putText(Image, Text, (2, Height), variables.FONT_TYPE, Fontscale, (0, 255, 0) if Class != "None" else (0, 0, 255), Thickness, cv2.LINE_AA)
                            GridImage[Y:Y + (Image.shape[0] - 1), X:X + (Image.shape[1] - 1)] = cv2.resize(Image, (Image.shape[1] - 1, Image.shape[0] - 1))

                        for i in range(NumRows + 1):
                            Y = i * Images[0].shape[0] - 1
                            if Y < 0:
                                Y = 0
                            cv2.line(GridImage, (0, Y), (GridWidth - 1, Y), (255, 255, 255), 1)
                        for i in range(NumCols + 1):
                            X = i * Images[0].shape[1] - 1
                            if X < 0:
                                X = 0
                            cv2.line(GridImage, (X, 0), (X, GridHeight - 1), (255, 255, 255), 1)

                        Frame = GridImage



                    CleanFrame = EmptyFrame.copy()

                    if len(CleanContent) != 0:

                        UpdatedCleanContent = []
                        for Item in CleanContent:
                            UpdatedItem = Item
                            for Rule in Rules:
                                if Item[5] == Rule["IfClass"]:
                                    for Combination in Combinations:
                                        if len(CANVAS_CONTENT) > Item[4]:
                                            if any(Point in Line for Line in Combination for Point in CANVAS_CONTENT[Item[4]]):
                                                if Rule["PartOfClass"] in [OtherItem[5] for OtherItem in CleanContent if OtherItem[4] == Combinations.index(Combination)]:
                                                    UpdatedItem = (Item[0], Item[1], Item[2], Item[3], Item[4], Rule["ThenClass"], Item[6])
                                                    break
                            if UpdatedItem[5] != "None":
                                UpdatedCleanContent.append(UpdatedItem)
                        CleanContent = UpdatedCleanContent


                        FinalCleanContent = []

                        for i in range(len(CleanContent)):
                            BoxA = CleanContent[i]
                            ShouldKeep = True

                            for j in range(len(FinalCleanContent)):
                                BoxB = FinalCleanContent[j]

                                xA = max(BoxA[0], BoxB[0])
                                yA = max(BoxA[1], BoxB[1])
                                xB = min(BoxA[2], BoxB[2])
                                yB = min(BoxA[3], BoxB[3])

                                interArea = max(0, xB - xA) * max(0, yB - yA)

                                BoxAArea = (BoxA[2] - BoxA[0]) * (BoxA[3] - BoxA[1])
                                BoxBArea = (BoxB[2] - BoxB[0]) * (BoxB[3] - BoxB[1])

                                IoU = interArea / float(BoxAArea + BoxBArea - interArea) if (BoxAArea + BoxBArea - interArea) > 0 else 0

                                if IoU > 0.5:
                                    if BoxA[6] > BoxB[6]:
                                        FinalCleanContent[j] = BoxA
                                    ShouldKeep = False
                                    break

                            if ShouldKeep:
                                FinalCleanContent.append(BoxA)

                        CleanContent = FinalCleanContent


                        AbsoluteMinX = min([MinX for (MinX, MinY, MaxX, MaxY, _, _, _) in CleanContent])
                        AbsoluteMinY = min([MinY for (MinX, MinY, MaxX, MaxY, _, _, _) in CleanContent])
                        AbsoluteMaxX = max([MaxX for (MinX, MinY, MaxX, MaxY, _, _, _) in CleanContent])
                        AbsoluteMaxY = max([MaxY for (MinX, MinY, MaxX, MaxY, _, _, _) in CleanContent])

                    for Item in CleanContent:
                        MinX, MinY, MaxX, MaxY, _, Class, Confidence = Item

                        ScaleX = ((CleanFrame.shape[1] - 1) / (AbsoluteMaxX - AbsoluteMinX)) if AbsoluteMaxX - AbsoluteMinX != 0 else 1e9
                        ScaleY = ((CleanFrame.shape[0] - 1)  / (AbsoluteMaxY - AbsoluteMinY)) if AbsoluteMaxY - AbsoluteMinY != 0 else 1e9
                        Scale = min(ScaleX, ScaleY)
                        XOffset = ((CleanFrame.shape[1] - 1) - (AbsoluteMaxX - AbsoluteMinX) * Scale) / 2
                        YOffset = ((CleanFrame.shape[0] - 1) - (AbsoluteMaxY - AbsoluteMinY) * Scale) / 2

                        X1 = round((MaxX - AbsoluteMinX) * Scale + XOffset)
                        X2 = round((MinX - AbsoluteMinX) * Scale + XOffset)
                        Y1 = round((MaxY - AbsoluteMinY) * Scale + YOffset)
                        Y2 = round((MinY - AbsoluteMinY) * Scale + YOffset)
                        Text, Fontscale, Thickness, Width, Height = uicomponents.GetTextSize(Class, 100, 20)
                        cv2.putText(CleanFrame, Text, (round((X1 + X2) / 2 - Width / 2), round((Y1 + Y2) / 2 - Height / 2)), variables.FONT_TYPE, Fontscale, (255, 255, 255), Thickness, cv2.LINE_AA)



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
        SimpleWindow.Show("PyTorch-Calculator Detection", CleanFrame)
    except:
        CrashReport("Analyze - Error in function Update.", str(traceback.format_exc()))