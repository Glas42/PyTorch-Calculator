#ifndef VARIABLES_H
#define VARIABLES_H

#include <opencv2/opencv.hpp>
#include <filesystem>
#include <algorithm>
#include <iostream>

extern std::string PATH;
extern std::string BUILD_TYPE;
extern int FONT_SIZE;
extern int FONT_TYPE;
extern int POPUP_HEIGHT;
extern int TITLE_BAR_HEIGHT;
extern std::string THEME;
extern std::vector<int> TEXT_COLOR;
extern std::vector<int> DRAW_COLOR;
extern std::vector<int> GRAYED_TEXT_COLOR;
extern std::vector<int> BACKGROUND_COLOR;
extern std::vector<int> TAB_BAR_COLOR;
extern std::vector<int> TAB_BUTTON_COLOR;
extern std::vector<int> TAB_BUTTON_HOVER_COLOR;
extern std::vector<int> TAB_BUTTON_SELECTED_COLOR;
extern std::vector<int> TAB_BUTTON_SELECTED_HOVER_COLOR;
extern std::vector<int> POPUP_COLOR;
extern std::vector<int> POPUP_HOVER_COLOR;
extern std::vector<int> POPUP_PROGRESS_COLOR;
extern std::vector<int> BUTTON_COLOR;
extern std::vector<int> BUTTON_HOVER_COLOR;
extern std::vector<int> BUTTON_SELECTED_COLOR;
extern std::vector<int> BUTTON_SELECTED_HOVER_COLOR;
extern std::vector<int> SWITCH_COLOR;
extern std::vector<int> SWITCH_KNOB_COLOR;
extern std::vector<int> SWITCH_HOVER_COLOR;
extern std::vector<int> SWITCH_ENABLED_COLOR;
extern std::vector<int> SWITCH_ENABLED_HOVER_COLOR;
extern std::vector<int> DROPDOWN_COLOR;
extern std::vector<int> DROPDOWN_HOVER_COLOR;

#endif