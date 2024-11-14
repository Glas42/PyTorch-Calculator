#include "ui.h"

void UI::Initialize() {
    // launch the input listener from UIComponets in a thread
    std::thread(UIComponents::InputListener).detach();
    FRAME = OpenCV::EmptyImage(700, 400, 3, BACKGROUND_COLOR[0], BACKGROUND_COLOR[1], BACKGROUND_COLOR[2]);
    OpenCV::ShowImage("PyTorch-Calculator", FRAME, false);
    OpenCV::SetWindowCaptionColor(L"PyTorch-Calculator", BACKGROUND_COLOR[0], BACKGROUND_COLOR[1], BACKGROUND_COLOR[2]);
    OpenCV::SetWindowBorderColor(L"PyTorch-Calculator", 200, 200, 200);
}

void UI::Example() {
    FRAME = OpenCV::EmptyImage(700, 400, 3, BACKGROUND_COLOR[0], BACKGROUND_COLOR[1], BACKGROUND_COLOR[2]);
    UIComponents::Label("PyTorch-Calculator", 0, 0, 700, 400, "Center", FONT_SIZE, TEXT_COLOR);
    UIComponents::Button("Press Me!", 100, 300, 600, 350, FONT_SIZE, 4, false, TEXT_COLOR, BUTTON_COLOR, BUTTON_HOVER_COLOR, BUTTON_SELECTED_COLOR, BUTTON_SELECTED_HOVER_COLOR);
    OpenCV::ShowImage("PyTorch-Calculator", FRAME, false);
}