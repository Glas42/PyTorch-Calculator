#ifndef VARIABLES_H
#define VARIABLES_H

#include <opencv2/opencv.hpp>
#include <filesystem>
#include <algorithm>
#include <iostream>

#include "opencv.h"

namespace Variables {
    extern std::string PATH;
    extern std::string BUILD_TYPE;
    extern std::string BOLD;
    extern std::string ITALIC;
    extern std::string UNDERLINE;
    extern std::string RED;
    extern std::string GRAY;
    extern std::string BLUE;
    extern std::string CYAN;
    extern std::string GREEN;
    extern std::string NORMAL;
    extern std::string YELLOW;
    extern std::string PURPLE;

    extern cv::Mat FRAME;

    extern std::string NAME;
    extern int FONT_SIZE;
    extern int FONT_TYPE;
    extern int POPUP_HEIGHT;
    extern int TITLE_BAR_HEIGHT;
    extern std::string THEME;
    extern cv::Scalar TEXT_COLOR;
    extern cv::Scalar DRAW_COLOR;
    extern cv::Scalar GRAYED_TEXT_COLOR;
    extern cv::Scalar BACKGROUND_COLOR;
    extern cv::Scalar TAB_BAR_COLOR;
    extern cv::Scalar TAB_BUTTON_COLOR;
    extern cv::Scalar TAB_BUTTON_HOVER_COLOR;
    extern cv::Scalar TAB_BUTTON_SELECTED_COLOR;
    extern cv::Scalar TAB_BUTTON_SELECTED_HOVER_COLOR;
    extern cv::Scalar POPUP_COLOR;
    extern cv::Scalar POPUP_HOVER_COLOR;
    extern cv::Scalar POPUP_PROGRESS_COLOR;
    extern cv::Scalar BUTTON_COLOR;
    extern cv::Scalar BUTTON_HOVER_COLOR;
    extern cv::Scalar BUTTON_SELECTED_COLOR;
    extern cv::Scalar BUTTON_SELECTED_HOVER_COLOR;
    extern cv::Scalar SWITCH_COLOR;
    extern cv::Scalar SWITCH_KNOB_COLOR;
    extern cv::Scalar SWITCH_HOVER_COLOR;
    extern cv::Scalar SWITCH_ENABLED_COLOR;
    extern cv::Scalar SWITCH_ENABLED_HOVER_COLOR;
    extern cv::Scalar DROPDOWN_COLOR;
    extern cv::Scalar DROPDOWN_HOVER_COLOR;
};

#endif