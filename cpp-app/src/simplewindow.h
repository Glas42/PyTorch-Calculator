#ifndef SIMPLEWINDOW_H
#define SIMPLEWINDOW_H

#include <filesystem>
#include <windows.h>
#include <iostream>
#include <string>
#include <tuple>

#include "variables.h"

class Window {
public:
    Window() = default;

    std::string GetName() const { return Name_; }
    void SetName(const std::string& Name) { Name_ = Name; }

    std::tuple<int, int> GetSize() const { return Size_; }
    void SetSize(std::tuple<int, int> Size) { Size_ = Size; }

    std::tuple<int, int> GetPosition() const { return Position_; }
    void SetPosition(std::tuple<int, int> Position) { Position_ = Position; }

    std::tuple<int, int, int> GetTitleBarColor() const { return TitleBarColor_; }
    void SetTitleBarColor(const std::tuple<int, int, int>& TitleBarColor) { TitleBarColor_ = TitleBarColor; }

    bool GetResizable() const { return Resizable_; }
    void SetResizable(bool Resizable) { Resizable_ = Resizable; }

    bool GetTopMost() const { return TopMost_; }
    void SetTopMost(bool TopMost) { TopMost_ = TopMost; }

    bool GetForeground() const { return Foreground_; }
    void SetForeground(bool Foreground) { Foreground_ = Foreground; }

    bool GetMinimized() const { return Minimized_; }
    void SetMinimized(bool Minimized) { Minimized_ = Minimized; }

    bool GetUndestroyable() const { return Undestroyable_; }
    void SetUndestroyable(bool Undestroyable) { Undestroyable_ = Undestroyable; }

    std::string GetIcon() const { return Icon_; }
    void SetIcon(const std::string& Icon) { Icon_ = Icon; }

    bool GetNoWarnings() const { return NoWarnings_; }
    void SetNoWarnings(bool NoWarnings) { NoWarnings_ = NoWarnings; }

    bool GetOpen() const { return Open_; }
    void SetOpen(bool Open) { Open_ = Open; }

    void* GetWindow() const { return Window_; }
    void SetWindow(void* Window) { Window_ = Window; }

private:
    std::string Name_;
    std::tuple<int, int> Size_ = std::make_tuple(0, 0);
    std::tuple<int, int> Position_ = std::make_tuple(0, 0);
    std::tuple<int, int, int> TitleBarColor_ = std::make_tuple(0, 0, 0);
    bool Resizable_ = true;
    bool TopMost_ = false;
    bool Foreground_ = true;
    bool Minimized_ = false;
    bool Undestroyable_ = false;
    std::string Icon_ = "";
    bool NoWarnings_ = false;
    bool Open_ = false;
    void* Window_ = nullptr;
};

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
    static void Create(std::string Name = "");
};

#endif