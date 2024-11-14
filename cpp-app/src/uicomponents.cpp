#include "uicomponents.h"

bool ForegroundWindow = true;
int FrameWidth = 0;
int FrameHeight = 0;
int MouseX = 0;
int MouseY = 0;
bool LeftClicked = false;
bool RightClicked = false;
bool LastLeftClicked = false;
bool LastRightClicked = false;

void UIComponents::InputListener() {
    HWND HWND;
    RECT RECT;
    POINT TopLeft, BottomRight, CursorPosition;
    while (true) {
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
        HWND = FindWindowW(NULL, L"PyTorch-Calculator");
        if (GetForegroundWindow() == HWND) {
            ForegroundWindow = true;
        } else {
            ForegroundWindow = false;
        }
        if (GetClientRect(HWND, &RECT)) {
            TopLeft.x = RECT.left;
            TopLeft.y = RECT.top;
            BottomRight.x = RECT.right;
            BottomRight.y = RECT.bottom;
            ClientToScreen(HWND, &TopLeft);
            ClientToScreen(HWND, &BottomRight);

            FrameWidth = BottomRight.x - TopLeft.x;
            FrameHeight = BottomRight.y - TopLeft.y;

            if (GetCursorPos(&CursorPosition)) {
                MouseX = CursorPosition.x - TopLeft.x;
                MouseY = CursorPosition.y - TopLeft.y;

                LastLeftClicked = LeftClicked;
                if (GetAsyncKeyState(VK_LBUTTON) & 0x8000) {
                    LeftClicked = true;
                } else {
                    LeftClicked = false;
                }
                LastRightClicked = RightClicked;
                if (GetAsyncKeyState(VK_RBUTTON) & 0x8000) {
                    RightClicked = true;
                } else {
                    RightClicked = false;
                }
            }

        }
    }
}

std::tuple<std::string, float, float, int, int> UIComponents::GetTextSize(std::string Text, float TextWidth, float FontSize) {
    float Fontscale = 1;
    float Thickness = 1;
    cv::Size Textsize = cv::getTextSize(Text, FONT_TYPE, Fontscale, Thickness, 0);
    int WidthCurrentText = static_cast<int>(Textsize.width);
    int HeightCurrentText = static_cast<int>(Textsize.height);
    int MaxCountCurrentText = 3;
    while (WidthCurrentText != TextWidth || HeightCurrentText > FontSize) {
        Fontscale *= min(TextWidth / Textsize.width, FontSize / Textsize.height);
        Textsize = cv::getTextSize(Text, FONT_TYPE, Fontscale, 1, 0);
        MaxCountCurrentText -= 1;
        if (MaxCountCurrentText <= 0) {
            break;
        }
    }
    Thickness = round(Fontscale * 2);
    if (Thickness <= 0) {
        Thickness = 1;
    }
    return std::make_tuple(Text, Fontscale, Thickness, static_cast<int>(Textsize.width), static_cast<int>(Textsize.height));
}

void UIComponents::Label(std::string Text, int X1, int Y1, int X2, int Y2, std::string Align, int Fontsize, cv::Scalar TextColor) {
    //Y1 += TITLE_BAR_HEIGHT;
    //Y2 += TITLE_BAR_HEIGHT;
    std::vector<std::string> Texts;
    std::stringstream ss(Text);
    std::string line;
    while (std::getline(ss, line, '\n')) {
        Texts.push_back(line);
    }
    float LineHeight = ((Y2 - Y1) / Texts.size());
    for (size_t i = 0; i < Texts.size(); i++) {
        const std::string& t = Texts[i];
        std::tuple<std::string, float, float, int, int> TextData = UIComponents::GetTextSize(t, X2 - X1, LineHeight / 1.5 < Fontsize ? LineHeight / 1.5 : Fontsize);
        float Fontscale = std::get<1>(TextData);
        float Thickness = std::get<2>(TextData);
        int Width = std::get<3>(TextData);
        int Height = std::get<4>(TextData);
        int X;
        if (Align == "Center") {
            X = round(X1 + (X2 - X1) / 2 - Width / 2);
        } else if (Align == "Left") {
            X = round(X1);
        } else if (Align == "Right") {
            X = round(X1 + (X2 - X1) - Width);
        }
        cv::putText(FRAME, Text, cv::Point(X, round(Y1 + (i + 0.5) * LineHeight + Height / 2)), FONT_TYPE, Fontscale, TextColor, Thickness, cv::LINE_AA);
    }
}

std::tuple<bool, bool, bool> UIComponents::Button(std::string Text, int X1, int Y1, int X2, int Y2, int Fontsize, int RoundCorners, bool ButtonSelected, cv::Scalar TextColor, cv::Scalar ButtonColor, cv::Scalar ButtonHoverColor, cv::Scalar ButtonSelectedColor, cv::Scalar ButtonSelectedHoverColor) {
    //Y1 += TITLE_BAR_HEIGHT;
    //Y2 += TITLE_BAR_HEIGHT;
    bool ButtonHovered;
    if (X1 <= MouseX && MouseX <= X2 && Y1 <= MouseY && MouseY <= Y2 && ForegroundWindow) {
        ButtonHovered = true;
    } else {
        ButtonHovered = false;
    }
    if (ButtonSelected == true) {
        if (ButtonHovered == true) {
            cv::rectangle(FRAME, cv::Point(round(X1 + RoundCorners / 2), round(Y1 + RoundCorners / 2)), cv::Point(round(X2 - RoundCorners / 2), round(Y2 - RoundCorners / 2)), ButtonSelectedHoverColor, RoundCorners, cv::LINE_AA);
            cv::rectangle(FRAME, cv::Point(round(X1 + RoundCorners / 2), round(Y1 + RoundCorners / 2)), cv::Point(round(X2 - RoundCorners / 2), round(Y2 - RoundCorners / 2)), ButtonSelectedHoverColor, -1, cv::LINE_AA);
        } else {
            cv::rectangle(FRAME, cv::Point(round(X1 + RoundCorners / 2), round(Y1 + RoundCorners / 2)), cv::Point(round(X2 - RoundCorners / 2), round(Y2 - RoundCorners / 2)), ButtonSelectedColor, RoundCorners, cv::LINE_AA);
            cv::rectangle(FRAME, cv::Point(round(X1 + RoundCorners / 2), round(Y1 + RoundCorners / 2)), cv::Point(round(X2 - RoundCorners / 2), round(Y2 - RoundCorners / 2)), ButtonSelectedColor, -1, cv::LINE_AA);
        }
    } else {
        if (ButtonHovered == true) {
            cv::rectangle(FRAME, cv::Point(round(X1 + RoundCorners / 2), round(Y1 + RoundCorners / 2)), cv::Point(round(X2 - RoundCorners / 2), round(Y2 - RoundCorners / 2)), ButtonHoverColor, RoundCorners, cv::LINE_AA);
            cv::rectangle(FRAME, cv::Point(round(X1 + RoundCorners / 2), round(Y1 + RoundCorners / 2)), cv::Point(round(X2 - RoundCorners / 2), round(Y2 - RoundCorners / 2)), ButtonHoverColor, -1, cv::LINE_AA);
        } else {
            cv::rectangle(FRAME, cv::Point(round(X1 + RoundCorners / 2), round(Y1 + RoundCorners / 2)), cv::Point(round(X2 - RoundCorners / 2), round(Y2 - RoundCorners / 2)), ButtonColor, RoundCorners, cv::LINE_AA);
            cv::rectangle(FRAME, cv::Point(round(X1 + RoundCorners / 2), round(Y1 + RoundCorners / 2)), cv::Point(round(X2 - RoundCorners / 2), round(Y2 - RoundCorners / 2)), ButtonColor, -1, cv::LINE_AA);
        }
    }
    std::tuple<std::string, float, float, int, int> TextData = UIComponents::GetTextSize(Text, round(X2 - X1), Fontsize);
    float Fontscale = std::get<1>(TextData);
    float Thickness = std::get<2>(TextData);
    int Width = std::get<3>(TextData);
    int Height = std::get<4>(TextData);
    cv::putText(FRAME, Text, cv::Point(round(X1 + (X2-X1) / 2 - Width / 2), round(Y1 + (Y2-Y1) / 2 + Height / 2)), FONT_TYPE, Fontscale, TextColor, Thickness, cv::LINE_AA);
    if (X1 <= MouseX && MouseX <= X2 && Y1 <= MouseY && MouseY <= Y2 && LeftClicked == false && LastLeftClicked == true) {
        return std::make_tuple(true, LeftClicked && ButtonHovered, ButtonHovered);
    } else {
        return std::make_tuple(false, LeftClicked && ButtonHovered, ButtonHovered);
    }
}