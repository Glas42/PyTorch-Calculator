from src.crashreport import CrashReport
import src.translate as translate
import src.variables as variables
import src.settings as settings
import threading
import traceback
import pynput
import math
import time
import cv2


ForegroundWindow = False
FrameWidth = None
FrameHeight = None
MouseX = None
MouseY = None
LeftClicked = False
RightClicked = False
LastLeftClicked = False
LastRightClicked = False

ScrollEventQueue = []
def HandleScrollEvents():
    try:
        global ScrollEventQueue
        with pynput.mouse.Events() as Events:
            while variables.BREAK == False:
                Event = Events.get()
                if isinstance(Event, pynput.mouse.Events.Scroll):
                    ScrollEventQueue.append(Event)
    except:
        CrashReport("UIComponents - Error in function HandleScrollEvents.", str(traceback.format_exc()))
ScrollEventThread = threading.Thread(target=HandleScrollEvents, daemon=True).start()


def GetTextSize(Text="NONE", TextWidth=100, Fontsize=variables.FONT_SIZE):
    try:
        global ForegroundWindow, FrameWidth, FrameHeight, MouseX, MouseY, LeftClicked, RightClicked, LastLeftClicked, LastRightClicked
        Fontscale = 1
        Textsize, _ = cv2.getTextSize(Text, variables.FONT_TYPE, Fontscale, 1)
        WidthCurrentText, HeightCurrentText = Textsize
        maxCountCurrentText = 3
        while WidthCurrentText != TextWidth or HeightCurrentText > Fontsize:
            Fontscale *= min(TextWidth / Textsize[0], Fontsize / Textsize[1])
            Textsize, _ = cv2.getTextSize(Text, variables.FONT_TYPE, Fontscale, 1)
            maxCountCurrentText -= 1
            if maxCountCurrentText <= 0:
                break
        Thickness = round(Fontscale * 2)
        if Thickness <= 0:
            Thickness = 1
        return Text, Fontscale, Thickness, Textsize[0], Textsize[1]
    except:
        CrashReport("UIComponents - Error in function GetTextSize.", str(traceback.format_exc()))
        return "", 1, 1, 100, 100


def Label(Text="NONE", X1=0, Y1=0, X2=100, Y2=100, Align="Center", Fontsize=variables.FONT_SIZE, TextColor=variables.TEXT_COLOR):
    try:
        global ForegroundWindow, FrameWidth, FrameHeight, MouseX, MouseY, LeftClicked, RightClicked, LastLeftClicked, LastRightClicked, ScrollEventQueue
        Y1 += variables.TITLE_BAR_HEIGHT
        Y2 += variables.TITLE_BAR_HEIGHT
        Texts = Text.split("\n")
        LineHeight = ((Y2-Y1) / len(Texts))
        for i, t in enumerate(Texts):
            t = translate.Translate(t)
            Text, Fontscale, Thickness, Width, Height = GetTextSize(t, round((X2-X1)), LineHeight / 1.5 if LineHeight / 1.5 < Fontsize else Fontsize)
            if Align == "Center":
                x = round(X1 + (X2-X1) / 2 - Width / 2)
            elif Align == "Left":
                x = round(X1)
            elif Align == "Right":
                x = round(X1 + (X2-X1) - Width)
            cv2.putText(variables.FRAME, Text, (x, round(Y1 + (i + 0.5) * LineHeight + Height / 2)), variables.FONT_TYPE, Fontscale, TextColor, Thickness, cv2.LINE_AA)
    except:
        CrashReport("UIComponents - Error in function Label.", str(traceback.format_exc()))
        return False, False, False


def Button(Text="NONE", X1=0, Y1=0, X2=100, Y2=100, Fontsize=variables.FONT_SIZE, RoundCorners=5, ButtonSelected=False, TextColor=variables.TEXT_COLOR, ButtonColor=variables.BUTTON_COLOR, ButtonHoverColor=variables.BUTTON_HOVER_COLOR, ButtonSelectedColor=variables.BUTTON_SELECTED_COLOR, ButtonSelectedHoverColor=variables.BUTTON_SELECTED_HOVER_COLOR):
    try:
        global ForegroundWindow, FrameWidth, FrameHeight, MouseX, MouseY, LeftClicked, RightClicked, LastLeftClicked, LastRightClicked, ScrollEventQueue
        Y1 += variables.TITLE_BAR_HEIGHT
        Y2 += variables.TITLE_BAR_HEIGHT
        Text = translate.Translate(Text)
        if X1 <= MouseX * FrameWidth <= X2 and Y1 <= MouseY * FrameHeight <= Y2 and ForegroundWindow and (variables.CONTEXT_MENU[0] == False or Text in str(variables.CONTEXT_MENU_ITEMS)):
            ButtonHovered = True
        else:
            ButtonHovered = False
        if ButtonSelected == True:
            if ButtonHovered == True:
                cv2.rectangle(variables.FRAME, (round(X1+RoundCorners/2), round(Y1+RoundCorners/2)), (round(X2-RoundCorners/2), round(Y2-RoundCorners/2)), ButtonSelectedHoverColor, RoundCorners, cv2.LINE_AA)
                cv2.rectangle(variables.FRAME, (round(X1+RoundCorners/2), round(Y1+RoundCorners/2)), (round(X2-RoundCorners/2), round(Y2-RoundCorners/2)), ButtonSelectedHoverColor, -1, cv2.LINE_AA)
            else:
                cv2.rectangle(variables.FRAME, (round(X1+RoundCorners/2), round(Y1+RoundCorners/2)), (round(X2-RoundCorners/2), round(Y2-RoundCorners/2)), ButtonSelectedColor, RoundCorners, cv2.LINE_AA)
                cv2.rectangle(variables.FRAME, (round(X1+RoundCorners/2), round(Y1+RoundCorners/2)), (round(X2-RoundCorners/2), round(Y2-RoundCorners/2)), ButtonSelectedColor, -1, cv2.LINE_AA)
        elif ButtonHovered == True:
            cv2.rectangle(variables.FRAME, (round(X1+RoundCorners/2), round(Y1+RoundCorners/2)), (round(X2-RoundCorners/2), round(Y2-RoundCorners/2)), ButtonHoverColor, RoundCorners, cv2.LINE_AA)
            cv2.rectangle(variables.FRAME, (round(X1+RoundCorners/2), round(Y1+RoundCorners/2)), (round(X2-RoundCorners/2), round(Y2-RoundCorners/2)), ButtonHoverColor, -1, cv2.LINE_AA)
        else:
            cv2.rectangle(variables.FRAME, (round(X1+RoundCorners/2), round(Y1+RoundCorners/2)), (round(X2-RoundCorners/2), round(Y2-RoundCorners/2)), ButtonColor, RoundCorners, cv2.LINE_AA)
            cv2.rectangle(variables.FRAME, (round(X1+RoundCorners/2), round(Y1+RoundCorners/2)), (round(X2-RoundCorners/2), round(Y2-RoundCorners/2)), ButtonColor, -1, cv2.LINE_AA)
        Text, Fontscale, Thickness, Width, Height = GetTextSize(Text, round((X2-X1)), Fontsize)
        cv2.putText(variables.FRAME, Text, (round(X1 + (X2-X1) / 2 - Width / 2), round(Y1 + (Y2-Y1) / 2 + Height / 2)), variables.FONT_TYPE, Fontscale, TextColor, Thickness, cv2.LINE_AA)
        if X1 <= MouseX * FrameWidth <= X2 and Y1 <= MouseY * FrameHeight <= Y2 and LeftClicked == False and LastLeftClicked == True and (variables.CONTEXT_MENU[0] == False or Text in str(variables.CONTEXT_MENU_ITEMS)):
            return True, LeftClicked and ButtonHovered, ButtonHovered
        else:
            return False, LeftClicked and ButtonHovered, ButtonHovered
    except:
        CrashReport("UIComponents - Error in function Button.", str(traceback.format_exc()))
        return False, False, False


def Switch(Text="NONE", X1=0, Y1=0, X2=100, Y2=100, SwitchWidth=40, SwitchHeight=20, TextPadding=10, State=False, Setting=None, Fontsize=variables.FONT_SIZE, TextColor=variables.TEXT_COLOR, SwitchColor=variables.SWITCH_COLOR, SwitchKnobColor=variables.SWITCH_KNOB_COLOR, SwitchHoverColor=variables.SWITCH_HOVER_COLOR, SwitchEnabledColor=variables.SWITCH_ENABLED_COLOR, SwitchEnabledHoverColor=variables.SWITCH_ENABLED_HOVER_COLOR):
    try:
        global ForegroundWindow, FrameWidth, FrameHeight, MouseX, MouseY, LeftClicked, RightClicked, LastLeftClicked, LastRightClicked, ScrollEventQueue
        CurrentTime = time.time()
        Y1 += variables.TITLE_BAR_HEIGHT
        Y2 += variables.TITLE_BAR_HEIGHT
        Text = translate.Translate(Text)
        if Text in variables.SWITCHES:
            State = variables.SWITCHES[Text][0]
        else:
            if Setting is not None:
                State = settings.Get(str(Setting[0]), str(Setting[1]), Setting[2])
            variables.SWITCHES[Text] = State, 0

        x = CurrentTime - variables.SWITCHES[Text][1]
        if x < 0.3333:
            x *= 3
            animationState = 1 - math.pow(2, -10 * x)
            variables.RENDER_FRAME = True
            if State == False:
                SwitchColor = SwitchColor[0] * animationState + SwitchEnabledColor[0] * (1 - animationState), SwitchColor[1] * animationState + SwitchEnabledColor[1] * (1 - animationState), SwitchColor[2] * animationState + SwitchEnabledColor[2] * (1 - animationState)
                SwitchHoverColor = SwitchHoverColor[0] * animationState + SwitchEnabledHoverColor[0] * (1 - animationState), SwitchHoverColor[1] * animationState + SwitchEnabledHoverColor[1] * (1 - animationState), SwitchHoverColor[2] * animationState + SwitchEnabledHoverColor[2] * (1 - animationState)
            else:
                SwitchEnabledColor = SwitchColor[0] * (1 - animationState) + SwitchEnabledColor[0] * animationState, SwitchColor[1] * (1 - animationState) + SwitchEnabledColor[1] * animationState, SwitchColor[2] * (1 - animationState) + SwitchEnabledColor[2] * animationState
                SwitchEnabledHoverColor = SwitchHoverColor[0] * (1 - animationState) + SwitchEnabledHoverColor[0] * animationState, SwitchHoverColor[1] * (1 - animationState) + SwitchEnabledHoverColor[1] * animationState, SwitchHoverColor[2] * (1 - animationState) + SwitchEnabledHoverColor[2] * animationState
        else:
            animationState = 1

        if X1 <= MouseX * FrameWidth <= X2 and Y1 <= MouseY * FrameHeight <= Y2 and ForegroundWindow and (variables.CONTEXT_MENU[0] == False or Text in str(variables.CONTEXT_MENU_ITEMS)):
            SwitchHovered = True
        else:
            SwitchHovered = False
        if SwitchHovered == True:
            if State == True:
                cv2.circle(variables.FRAME, (round(X1+SwitchHeight/2), round((Y1+Y2)/2)), round(SwitchHeight/2), SwitchEnabledHoverColor, -1, cv2.LINE_AA)
                cv2.circle(variables.FRAME, (round(X1+SwitchWidth-SwitchHeight/2), round((Y1+Y2)/2)), round(SwitchHeight/2), SwitchEnabledHoverColor, -1, cv2.LINE_AA)
                cv2.rectangle(variables.FRAME, (round(X1+SwitchHeight/2+1), round((Y1+Y2)/2-SwitchHeight/2)), (round(X1+SwitchWidth-SwitchHeight/2-1), round((Y1+Y2)/2+SwitchHeight/2)), SwitchEnabledHoverColor, -1, cv2.LINE_AA)
                if animationState < 1:
                    cv2.circle(variables.FRAME, (round(X1+SwitchHeight/2+(SwitchWidth-SwitchHeight)*animationState), round((Y1+Y2)/2)), round(SwitchHeight/2.5), SwitchKnobColor, -1, cv2.LINE_AA)
                else:
                    cv2.circle(variables.FRAME, (round(X1+SwitchWidth-SwitchHeight/2), round((Y1+Y2)/2)), round(SwitchHeight/2.5), SwitchKnobColor, -1, cv2.LINE_AA)
            else:
                cv2.circle(variables.FRAME, (round(X1+SwitchHeight/2), round((Y1+Y2)/2)), round(SwitchHeight/2), SwitchHoverColor, -1, cv2.LINE_AA)
                cv2.circle(variables.FRAME, (round(X1+SwitchWidth-SwitchHeight/2), round((Y1+Y2)/2)), round(SwitchHeight/2), SwitchHoverColor, -1, cv2.LINE_AA)
                cv2.rectangle(variables.FRAME, (round(X1+SwitchHeight/2+1), round((Y1+Y2)/2-SwitchHeight/2)), (round(X1+SwitchWidth-SwitchHeight/2-1), round((Y1+Y2)/2+SwitchHeight/2)), SwitchHoverColor, -1, cv2.LINE_AA)
                if animationState < 1:
                    cv2.circle(variables.FRAME, (round(X1+SwitchHeight/2+(SwitchWidth-SwitchHeight)*(1-animationState)), round((Y1+Y2)/2)), round(SwitchHeight/2.5), SwitchKnobColor, -1, cv2.LINE_AA)
                else:
                    cv2.circle(variables.FRAME, (round(X1+SwitchHeight/2), round((Y1+Y2)/2)), round(SwitchHeight/2.5), SwitchKnobColor, -1, cv2.LINE_AA)
        else:
            if State == True:
                cv2.circle(variables.FRAME, (round(X1+SwitchHeight/2), round((Y1+Y2)/2)), round(SwitchHeight/2), SwitchEnabledColor, -1, cv2.LINE_AA)
                cv2.circle(variables.FRAME, (round(X1+SwitchWidth-SwitchHeight/2), round((Y1+Y2)/2)), round(SwitchHeight/2), SwitchEnabledColor, -1, cv2.LINE_AA)
                cv2.rectangle(variables.FRAME, (round(X1+SwitchHeight/2+1), round((Y1+Y2)/2-SwitchHeight/2)), (round(X1+SwitchWidth-SwitchHeight/2-1), round((Y1+Y2)/2+SwitchHeight/2)), SwitchEnabledColor, -1, cv2.LINE_AA)
                if animationState < 1:
                    cv2.circle(variables.FRAME, (round(X1+SwitchHeight/2+(SwitchWidth-SwitchHeight)*animationState), round((Y1+Y2)/2)), round(SwitchHeight/2.5), SwitchKnobColor, -1, cv2.LINE_AA)
                else:
                    cv2.circle(variables.FRAME, (round(X1+SwitchWidth-SwitchHeight/2), round((Y1+Y2)/2)), round(SwitchHeight/2.5), SwitchKnobColor, -1, cv2.LINE_AA)
            else:
                cv2.circle(variables.FRAME, (round(X1+SwitchHeight/2), round((Y1+Y2)/2)), round(SwitchHeight/2), SwitchColor, -1, cv2.LINE_AA)
                cv2.circle(variables.FRAME, (round(X1+SwitchWidth-SwitchHeight/2), round((Y1+Y2)/2)), round(SwitchHeight/2), SwitchColor, -1, cv2.LINE_AA)
                cv2.rectangle(variables.FRAME, (round(X1+SwitchHeight/2+1), round((Y1+Y2)/2-SwitchHeight/2)), (round(X1+SwitchWidth-SwitchHeight/2-1), round((Y1+Y2)/2+SwitchHeight/2)), SwitchColor, -1, cv2.LINE_AA)
                if animationState < 1:
                    cv2.circle(variables.FRAME, (round(X1+SwitchHeight/2+(SwitchWidth-SwitchHeight)*(1-animationState)), round((Y1+Y2)/2)), round(SwitchHeight/2.5), SwitchKnobColor, -1, cv2.LINE_AA)
                else:
                    cv2.circle(variables.FRAME, (round(X1+SwitchHeight/2), round((Y1+Y2)/2)), round(SwitchHeight/2.5), SwitchKnobColor, -1, cv2.LINE_AA)
        Text, Fontscale, Thickness, Width, Height = GetTextSize(Text, round((X2-X1)), Fontsize)
        cv2.putText(variables.FRAME, Text, (round(X1 + SwitchWidth + TextPadding), round(Y1 + (Y2-Y1) / 2 + Height / 2)), variables.FONT_TYPE, Fontscale, TextColor, Thickness, cv2.LINE_AA)
        if X1 <= MouseX * FrameWidth <= X2 and Y1 <= MouseY * FrameHeight <= Y2 and LeftClicked == False and LastLeftClicked == True and (variables.CONTEXT_MENU[0] == False or Text in str(variables.CONTEXT_MENU_ITEMS)):
            if Setting is not None:
                variables.SWITCHES[Text] = not State, CurrentTime
                settings.Set(str(Setting[0]), str(Setting[1]), not State)
            return True, LeftClicked and SwitchHovered, SwitchHovered
        else:
            return False, LeftClicked and SwitchHovered, SwitchHovered
    except:
        CrashReport("UIComponents - Error in function Switch.", str(traceback.format_exc()))
        return False, False, False


def Dropdown(Text="NONE", Items=["NONE"], DefaultItem=0, X1=0, Y1=0, X2=100, Y2=100, DropdownHeight=100, DropdownPadding=5, RoundCorners=5, Fontsize=variables.FONT_SIZE, TextColor=variables.TEXT_COLOR, grayedTextColor=variables.GRAYED_TEXT_COLOR, DropdownColor=variables.DROPDOWN_COLOR, DropdownHoverColor=variables.DROPDOWN_HOVER_COLOR):
    try:
        global ForegroundWindow, FrameWidth, FrameHeight, MouseX, MouseY, LeftClicked, RightClicked, LastLeftClicked, LastRightClicked, ScrollEventQueue
        Y1 += variables.TITLE_BAR_HEIGHT
        Y2 += variables.TITLE_BAR_HEIGHT
        if Text not in variables.DROPDOWNS:
            DefaultItem = int(max(min(DefaultItem, len(Items) - 1), 0))
            variables.DROPDOWNS[Text] = False, settings.Get("DropdownSelections", str(Text), DefaultItem)

        DropdownSelected, SelectedItem = variables.DROPDOWNS[Text]

        if X1 <= MouseX * FrameWidth <= X2 and Y1 <= MouseY * FrameHeight <= Y2 + ((DropdownHeight + DropdownPadding) if DropdownSelected else 0) and ForegroundWindow and (variables.CONTEXT_MENU[0] == False or Text in str(variables.CONTEXT_MENU_ITEMS)):
            DropdownHovered = True
            DropdownPressed = LeftClicked
            DropdownChanged = True if LastLeftClicked == True and LeftClicked == False and DropdownSelected == True else False
            DropdownSelected = not DropdownSelected if LastLeftClicked == True and LeftClicked == False else DropdownSelected
        else:
            DropdownHovered = False
            DropdownPressed = False
            DropdownChanged =  DropdownSelected
            DropdownSelected = False

        if DropdownHovered == True:
            cv2.rectangle(variables.FRAME, (round(X1+RoundCorners/2), round(Y1+RoundCorners/2)), (round(X2-RoundCorners/2), round(Y2-RoundCorners/2)), DropdownHoverColor, RoundCorners, cv2.LINE_AA)
            cv2.rectangle(variables.FRAME, (round(X1+RoundCorners/2), round(Y1+RoundCorners/2)), (round(X2-RoundCorners/2), round(Y2-RoundCorners/2)), DropdownHoverColor, -1, cv2.LINE_AA)
        else:
            cv2.rectangle(variables.FRAME, (round(X1+RoundCorners/2), round(Y1+RoundCorners/2)), (round(X2-RoundCorners/2), round(Y2-RoundCorners/2)), DropdownColor, RoundCorners, cv2.LINE_AA)
            cv2.rectangle(variables.FRAME, (round(X1+RoundCorners/2), round(Y1+RoundCorners/2)), (round(X2-RoundCorners/2), round(Y2-RoundCorners/2)), DropdownColor, -1, cv2.LINE_AA)
        if DropdownSelected == True:
            cv2.rectangle(variables.FRAME, (round(X1+RoundCorners/2), round(Y2+DropdownPadding+RoundCorners/2)), (round(X2-RoundCorners/2), round(Y2+DropdownHeight+DropdownPadding-RoundCorners/2)), DropdownHoverColor, RoundCorners, cv2.LINE_AA)
            cv2.rectangle(variables.FRAME, (round(X1+RoundCorners/2), round(Y2+DropdownPadding+RoundCorners/2)), (round(X2-RoundCorners/2), round(Y2+DropdownHeight+DropdownPadding-RoundCorners/2)), DropdownHoverColor, -1, cv2.LINE_AA)

            _, _, Thickness, _, _ = GetTextSize()
            Padding = (Y2 + Y1) / 2 - variables.FONT_SIZE / 4 - Y1
            Height = round(Y2 - Padding) - round(Y1 + Padding)
            cv2.line(variables.FRAME, (round(X2 - Padding - Height), round(Y1 + Padding)), (round(X2 - Padding), round(Y2 - Padding)), TextColor, Thickness, cv2.LINE_AA)
            cv2.line(variables.FRAME, (round(X2 - Padding - Height), round(Y1 + Padding)), (round(X2 - Padding  - Height * 2), round(Y2 - Padding)), TextColor, Thickness, cv2.LINE_AA)

            for Event in ScrollEventQueue:
                if Event.dy > 0:
                    SelectedItem = (SelectedItem - 1) if SelectedItem > 0 else 0
                elif Event.dy < 0:
                    SelectedItem = (SelectedItem + 1) if SelectedItem < len(Items) - 1 else len(Items) - 1
            ScrollEventQueue = []

            for i in range(3):
                LineHeight = (DropdownHeight / 3)
                index = SelectedItem - 1 + i
                if index >= len(Items):
                    index = -1
                if index < 0:
                    index = -1
                if index == -1:
                    Item = ""
                else:
                    Item = translate.Translate(Items[index])
                if i == 1:
                    ItemText = "> " + Item + " <"
                else:
                    ItemText = Item
                ItemText, Fontscale, Thickness, Width, Height = GetTextSize(ItemText, round((X2-X1)), LineHeight / 1.5 if LineHeight / 1.5 < Fontsize else Fontsize)
                cv2.putText(variables.FRAME, ItemText, (round(X1 + (X2-X1) / 2 - Width / 2), round(Y2 + DropdownPadding + (i + 0.5) * LineHeight + Height / 2)), variables.FONT_TYPE, Fontscale, TextColor if i == 1 else grayedTextColor, Thickness, cv2.LINE_AA)

        else:

            _, _, Thickness, _, _ = GetTextSize()
            Padding = (Y2 + Y1) / 2 - variables.FONT_SIZE / 4 - Y1
            Height = round(Y2 - Padding) - round(Y1 + Padding)
            cv2.line(variables.FRAME, (round(X2 - Padding - Height), round(Y2 - Padding)), (round(X2 - Padding), round(Y1 + Padding)), TextColor, Thickness, cv2.LINE_AA)
            cv2.line(variables.FRAME, (round(X2 - Padding - Height), round(Y2 - Padding)), (round(X2 - Padding  - Height * 2), round(Y1 + Padding)), TextColor, Thickness, cv2.LINE_AA)

        TextTranslated = translate.Translate(Text)
        TextTranslated, Fontscale, Thickness, Width, Height = GetTextSize(TextTranslated, round((X2-X1)), Fontsize)
        cv2.putText(variables.FRAME, TextTranslated, (round(X1 + (X2-X1) / 2 - Width / 2), round(Y1 + (Y2-Y1) / 2 + Height / 2)), variables.FONT_TYPE, Fontscale, TextColor, Thickness, cv2.LINE_AA)

        variables.DROPDOWNS[Text] = DropdownSelected, SelectedItem
        if DropdownChanged:
            settings.Set("DropdownSelections", str(Text), int(SelectedItem))
        if DropdownSelected:
            variables.RENDER_FRAME = True

        if DropdownChanged:
            DropdownChanged = (variables.CONTEXT_MENU[0] == False or Text in str(variables.CONTEXT_MENU_ITEMS))

        return DropdownChanged, DropdownPressed, DropdownHovered
    except:
        CrashReport("UIComponents - Error in function Dropdown.", str(traceback.format_exc()))
        return False, False, False


def Image(Image="NumpyArrayImage",X1=0, Y1=0, X2=100, Y2=100):
    try:
        if type(Image) == type(None):
            return
        if Image.shape[2] != 3:
            Image = cv2.cvtColor(Image, cv2.COLOR_GRAY2BGR)
        Y1 += variables.TITLE_BAR_HEIGHT
        Y2 += variables.TITLE_BAR_HEIGHT
        variables.FRAME[Y1:Y2 + 1, X1:X2 + 1] = Image
    except:
        CrashReport("UIComponents - Error in function Image.", str(traceback.format_exc()))