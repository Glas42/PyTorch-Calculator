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
        int Fontsize=Variables::FONT_SIZE,
        cv::Scalar TextColor=Variables::TEXT_COLOR);
    static std::tuple<bool, bool, bool> Button(std::string Text="NONE",
        int X1=0,
        int Y1=0,
        int X2=100,
        int Y2=100,
        int Fontsize=11,
        int RoundCorners=5,
        bool ButtonSelected=false,
        cv::Scalar TextColor=Variables::TEXT_COLOR,
        cv::Scalar ButtonColor=Variables::BUTTON_COLOR,
        cv::Scalar ButtonHoverColor=Variables::BUTTON_HOVER_COLOR,
        cv::Scalar ButtonSelectedColor=Variables::BUTTON_SELECTED_COLOR,
        cv::Scalar ButtonSelectedHoverColor=Variables::BUTTON_SELECTED_HOVER_COLOR);
};

#endif