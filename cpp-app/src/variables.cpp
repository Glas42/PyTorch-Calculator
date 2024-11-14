#include "variables.h"

// This needs to be here for some reason
#define WIN32_LEAN_AND_MEAN
#define VC_EXTRALEAN
#include <Windows.h>


std::string GetExePath() {
    std::string PATH = "";
    wchar_t wc[260] = {0};
    GetModuleFileNameW(NULL, wc, 260);
    std::wstring ws(wc);
    transform(ws.begin(), ws.end(), back_inserter(PATH), [](wchar_t c) { return (char)c; });
    return PATH.substr(0, PATH.rfind("\\") + 1);
}

std::string PATH = GetExePath();


#ifdef BUILD_TYPE_RELEASE
    std::string BUILD_TYPE = "Release";
#elif defined(BUILD_TYPE_DEBUG)
    std::string BUILD_TYPE = "Debug";
#endif


int FONT_SIZE = 11;
int FONT_TYPE = cv::FONT_HERSHEY_SIMPLEX;
int POPUP_HEIGHT = 50;
int TITLE_BAR_HEIGHT = 50;

std::string THEME = "Dark";
std::vector<int> TEXT_COLOR = THEME == "Dark" ? std::vector<int>{255, 255, 255} : std::vector<int>{0, 0, 0};
std::vector<int> DRAW_COLOR = THEME == "Dark" ? std::vector<int>{255, 255, 255} : std::vector<int>{0, 0, 0};
std::vector<int> GRAYED_TEXT_COLOR = THEME == "Dark" ? std::vector<int>{155, 155, 155} : std::vector<int>{100, 100, 100};
std::vector<int> BACKGROUND_COLOR = THEME == "Dark" ? std::vector<int>{28, 28, 28} : std::vector<int>{250, 250, 250};
std::vector<int> TAB_BAR_COLOR = THEME == "Dark" ? std::vector<int>{47, 47, 47} : std::vector<int>{231, 231, 231};
std::vector<int> TAB_BUTTON_COLOR = THEME == "Dark" ? std::vector<int>{47, 47, 47} : std::vector<int>{231, 231, 231};
std::vector<int> TAB_BUTTON_HOVER_COLOR = THEME == "Dark" ? std::vector<int>{41, 41, 41} : std::vector<int>{244, 244, 244};
std::vector<int> TAB_BUTTON_SELECTED_COLOR = THEME == "Dark" ? std::vector<int>{28, 28, 28} : std::vector<int>{250, 250, 250};
std::vector<int> TAB_BUTTON_SELECTED_HOVER_COLOR = THEME == "Dark" ? std::vector<int>{28, 28, 28} : std::vector<int>{250, 250, 250};
std::vector<int> POPUP_COLOR = THEME == "Dark" ? std::vector<int>{42, 42, 42} : std::vector<int>{236, 236, 236};
std::vector<int> POPUP_HOVER_COLOR = THEME == "Dark" ? std::vector<int>{42, 42, 42} : std::vector<int>{236, 236, 236};
std::vector<int> POPUP_PROGRESS_COLOR = THEME == "Dark" ? std::vector<int>{255, 200, 87} : std::vector<int>{184, 95, 0};
std::vector<int> BUTTON_COLOR = THEME == "Dark" ? std::vector<int>{42, 42, 42} : std::vector<int>{236, 236, 236};
std::vector<int> BUTTON_HOVER_COLOR = THEME == "Dark" ? std::vector<int>{47, 47, 47} : std::vector<int>{231, 231, 231};
std::vector<int> BUTTON_SELECTED_COLOR = THEME == "Dark" ? std::vector<int>{28, 28, 28} : std::vector<int>{250, 250, 250};
std::vector<int> BUTTON_SELECTED_HOVER_COLOR = THEME == "Dark" ? std::vector<int>{28, 28, 28} : std::vector<int>{250, 250, 250};
std::vector<int> SWITCH_COLOR = THEME == "Dark" ? std::vector<int>{70, 70, 70} : std::vector<int>{208, 208, 208};
std::vector<int> SWITCH_KNOB_COLOR = THEME == "Dark" ? std::vector<int>{28, 28, 28} : std::vector<int>{250, 250, 250};
std::vector<int> SWITCH_HOVER_COLOR = THEME == "Dark" ? std::vector<int>{70, 70, 70} : std::vector<int>{208, 208, 208};
std::vector<int> SWITCH_ENABLED_COLOR = THEME == "Dark" ? std::vector<int>{255, 200, 87} : std::vector<int>{184, 95, 0};
std::vector<int> SWITCH_ENABLED_HOVER_COLOR = THEME == "Dark" ? std::vector<int>{255, 200, 87} : std::vector<int>{184, 95, 0};
std::vector<int> DROPDOWN_COLOR = THEME == "Dark" ? std::vector<int>{42, 42, 42} : std::vector<int>{236, 236, 236};
std::vector<int> DROPDOWN_HOVER_COLOR = THEME == "Dark" ? std::vector<int>{47, 47, 47} : std::vector<int>{231, 231, 231};