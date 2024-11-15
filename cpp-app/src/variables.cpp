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


std::string BOLD = "\033[1m";
std::string ITALIC = "\033[3m";
std::string UNDERLINE = "\033[4m";

std::string RED = "\033[91m";
std::string GRAY = "\033[90m";
std::string BLUE = "\033[94m";
std::string CYAN = "\033[96m";
std::string GREEN = "\033[92m";
std::string NORMAL = "\033[0m";
std::string YELLOW = "\033[93m";
std::string PURPLE = "\033[95m";


int FONT_SIZE = 11;
int FONT_TYPE = cv::FONT_HERSHEY_SIMPLEX;
int POPUP_HEIGHT = 50;
int TITLE_BAR_HEIGHT = 50;

cv::Mat FRAME = OpenCV::EmptyImage(700, 400, 3, 0, 0, 0);

std::string THEME = "Dark";
cv::Scalar TEXT_COLOR = THEME == "Dark" ? cv::Scalar(255, 255, 255) : cv::Scalar(0, 0, 0);
cv::Scalar DRAW_COLOR = THEME == "Dark" ? cv::Scalar(255, 255, 255) : cv::Scalar(0, 0, 0);
cv::Scalar GRAYED_TEXT_COLOR = THEME == "Dark" ? cv::Scalar(155, 155, 155) : cv::Scalar(100, 100, 100);
cv::Scalar BACKGROUND_COLOR = THEME == "Dark" ? cv::Scalar(28, 28, 28) : cv::Scalar(250, 250, 250);
cv::Scalar TAB_BAR_COLOR = THEME == "Dark" ? cv::Scalar(47, 47, 47) : cv::Scalar(231, 231, 231);
cv::Scalar TAB_BUTTON_COLOR = THEME == "Dark" ? cv::Scalar(47, 47, 47) : cv::Scalar(231, 231, 231);
cv::Scalar TAB_BUTTON_HOVER_COLOR = THEME == "Dark" ? cv::Scalar(41, 41, 41) : cv::Scalar(244, 244, 244);
cv::Scalar TAB_BUTTON_SELECTED_COLOR = THEME == "Dark" ? cv::Scalar(28, 28, 28) : cv::Scalar(250, 250, 250);
cv::Scalar TAB_BUTTON_SELECTED_HOVER_COLOR = THEME == "Dark" ? cv::Scalar(28, 28, 28) : cv::Scalar(250, 250, 250);
cv::Scalar POPUP_COLOR = THEME == "Dark" ? cv::Scalar(42, 42, 42) : cv::Scalar(236, 236, 236);
cv::Scalar POPUP_HOVER_COLOR = THEME == "Dark" ? cv::Scalar(42, 42, 42) : cv::Scalar(236, 236, 236);
cv::Scalar POPUP_PROGRESS_COLOR = THEME == "Dark" ? cv::Scalar(255, 200, 87) : cv::Scalar(184, 95, 0);
cv::Scalar BUTTON_COLOR = THEME == "Dark" ? cv::Scalar(42, 42, 42) : cv::Scalar(236, 236, 236);
cv::Scalar BUTTON_HOVER_COLOR = THEME == "Dark" ? cv::Scalar(47, 47, 47) : cv::Scalar(231, 231, 231);
cv::Scalar BUTTON_SELECTED_COLOR = THEME == "Dark" ? cv::Scalar(28, 28, 28) : cv::Scalar(250, 250, 250);
cv::Scalar BUTTON_SELECTED_HOVER_COLOR = THEME == "Dark" ? cv::Scalar(28, 28, 28) : cv::Scalar(250, 250, 250);
cv::Scalar SWITCH_COLOR = THEME == "Dark" ? cv::Scalar(70, 70, 70) : cv::Scalar(208, 208, 208);
cv::Scalar SWITCH_KNOB_COLOR = THEME == "Dark" ? cv::Scalar(28, 28, 28) : cv::Scalar(250, 250, 250);
cv::Scalar SWITCH_HOVER_COLOR = THEME == "Dark" ? cv::Scalar(70, 70, 70) : cv::Scalar(208, 208, 208);
cv::Scalar SWITCH_ENABLED_COLOR = THEME == "Dark" ? cv::Scalar(255, 200, 87) : cv::Scalar(184, 95, 0);
cv::Scalar SWITCH_ENABLED_HOVER_COLOR = THEME == "Dark" ? cv::Scalar(255, 200, 87) : cv::Scalar(184, 95, 0);
cv::Scalar DROPDOWN_COLOR = THEME == "Dark" ? cv::Scalar(42, 42, 42) : cv::Scalar(236, 236, 236);
cv::Scalar DROPDOWN_HOVER_COLOR = THEME == "Dark" ? cv::Scalar(47, 47, 47) : cv::Scalar(231, 231, 231);