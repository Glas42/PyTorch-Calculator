#include "ui.h"

void UI::Initialize() {
    // launch the input listener from UIComponets in a thread
    std::thread(UIComponents::InputListener).detach();
    Variables::FRAME = OpenCV::EmptyImage(700, 400, 3, Variables::BACKGROUND_COLOR[0], Variables::BACKGROUND_COLOR[1], Variables::BACKGROUND_COLOR[2]);
    OpenCV::ShowImage("PyTorch-Calculator", Variables::FRAME, false);
    OpenCV::SetWindowCaptionColor(L"PyTorch-Calculator", Variables::BACKGROUND_COLOR[0], Variables::BACKGROUND_COLOR[1], Variables::BACKGROUND_COLOR[2]);
    OpenCV::SetWindowBorderColor(L"PyTorch-Calculator", 200, 200, 200);
}

void UI::Example() {
    if (FindWindowW(NULL, L"PyTorch-Calculator") == NULL) {
        UI::Initialize();
    }
    Variables::FRAME = OpenCV::EmptyImage(700, 400, 3, Variables::BACKGROUND_COLOR[0], Variables::BACKGROUND_COLOR[1], Variables::BACKGROUND_COLOR[2]);
    UIComponents::Label("PyTorch-Calculator", 0, 0, 700, 400, "Center", Variables::FONT_SIZE, Variables::TEXT_COLOR);
    UIComponents::Button("Press Me!", 100, 300, 600, 350, Variables::FONT_SIZE, 4, false, Variables::TEXT_COLOR, Variables::BUTTON_COLOR, Variables::BUTTON_HOVER_COLOR, Variables::BUTTON_SELECTED_COLOR, Variables::BUTTON_SELECTED_HOVER_COLOR);
    OpenCV::ShowImage("PyTorch-Calculator", Variables::FRAME, false);
}