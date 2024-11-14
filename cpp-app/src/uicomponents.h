#ifndef UICOMPONENTS_H
#define UICOMPONENTS_H

#include "uicomponents.h"
#include "variables.h"
#include "windows.h"
#include "opencv.h"

class UIComponents {
public:
    static void InputListener();
    static std::tuple<std::string, float, float, int, int> GetTextSize(std::string Text="NONE", float TextWidth=100, float FontSize=11);
    static void Label(std::string Text="NONE",
        int X1=0,
        int Y1=0,
        int X2=100,
        int Y2=100,
        std::string Align="Center",
        int Fontsize=FONT_SIZE,
        cv::Scalar TextColor=TEXT_COLOR);
    static std::tuple<bool, bool, bool> Button(std::string Text="NONE",
        int X1=0,
        int Y1=0,
        int X2=100,
        int Y2=100,
        int Fontsize=11,
        int RoundCorners=5,
        bool ButtonSelected=false,
        cv::Scalar TextColor=TEXT_COLOR,
        cv::Scalar ButtonColor=BUTTON_COLOR,
        cv::Scalar ButtonHoverColor=BUTTON_HOVER_COLOR,
        cv::Scalar ButtonSelectedColor=BUTTON_SELECTED_COLOR,
        cv::Scalar ButtonSelectedHoverColor=BUTTON_SELECTED_HOVER_COLOR);
};

#endif