#ifndef OPENCV_H
#define OPENCV_H

#include <opencv2/opencv.hpp>
#include <windows.h>
#include <dwmapi.h>
#include <string>

#pragma comment(lib, "dwmapi.lib")

class OpenCV {
public:
    static void ShowImage(std::string Name, cv::Mat Frame, bool Wait = false);
    static cv::Mat EmptyImage(int Width, int Height, int Channels, int Red = 0, int Green = 0, int Blue = 0);
    static void SetWindowCaptionColor(const wchar_t* Name, int Red = 0, int Green = 0, int Blue = 0);
    static void SetWindowBorderColor(const wchar_t* Name, int Red = 0, int Green = 0, int Blue = 0);
};

#endif