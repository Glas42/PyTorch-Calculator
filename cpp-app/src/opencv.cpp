#include "opencv.h"

void OpenCV::ShowImage(std::string Name, cv::Mat Frame, bool Wait) {
    cv::imshow(Name, Frame);
    if (Wait) {
        cv::waitKey(0);
    } else {
        cv::waitKey(1);
    }
}

cv::Mat OpenCV::EmptyImage(int Width, int Height, int Channels, int Red, int Green, int Blue) {
    cv::Mat Image(Height, Width, CV_8UC(Channels), Channels == 3 ? cv::Scalar(Blue, Green, Red) : cv::Scalar::all(0));
    return Image;
}

void OpenCV::SetWindowCaptionColor(const wchar_t* Name, int Red, int Green, int Blue) {
    HWND HWND = FindWindowW(NULL, Name);
    std::uint32_t CaptionColor[3] = {Blue, Green, Red};
	std::uint32_t ConvertedCaptionColor = (CaptionColor[0] << 16) | (CaptionColor[1] << 8) | CaptionColor[2];
	DwmSetWindowAttribute(HWND, DWMWA_CAPTION_COLOR, &ConvertedCaptionColor, sizeof(ConvertedCaptionColor));
}

void OpenCV::SetWindowBorderColor(const wchar_t* Name, int Red, int Green, int Blue) {
    HWND HWND = FindWindowW(NULL, Name);
	std::uint32_t BorderColor[3] = {Blue, Green, Red};
	std::uint32_t ConvertedBorderColor = (BorderColor[0] << 16) | (BorderColor[1] << 8) | BorderColor[2];
	DwmSetWindowAttribute(HWND, DWMWA_BORDER_COLOR, &ConvertedBorderColor, sizeof(ConvertedBorderColor));
}