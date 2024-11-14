#ifndef UICOMPONENTS_H
#define UICOMPONENTS_H

#include "uicomponents.h"
#include "variables.h"
#include "opencv.h"

class UIComponents {
public:
    static void Button(std::string Text="NONE",
        int X1=0,
        int Y1=0,
        int X2=100,
        int Y2=100,
        int Fontsize=11,
        int RoundCorners=5,
        bool ButtonSelected=false,
        std::vector<int> TextColor=TEXT_COLOR,
        std::vector<int> ButtonColor=BUTTON_COLOR,
        std::vector<int> ButtonHoverColor=BUTTON_HOVER_COLOR,
        std::vector<int> ButtonSelectedColor=BUTTON_SELECTED_COLOR,
        std::vector<int> ButtonSelectedHoverColor=BUTTON_SELECTED_HOVER_COLOR);

};

#endif