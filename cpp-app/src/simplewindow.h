#ifndef SIMPLEWINDOW_H
#define SIMPLEWINDOW_H

#include <windows.h>
#include <iostream>
#include <string>
#include <tuple>

#include "variables.h"

class SimpleWindow {
public:
    static bool Initialize(std::string Name = "",
        std::tuple<int, int> Size = std::make_tuple(0, 0),
        std::tuple<int, int> Position = std::make_tuple(0, 0),
        std::tuple<int, int, int> TitleBarColor = std::make_tuple(0, 0, 0),
        bool Resizable = true,
        bool TopMost = false,
        bool Foreground = true,
        bool Minimized = false,
        bool Undestroyable = false,
        std::string Icon = "",
        bool NoWarnings = false);
};

#endif