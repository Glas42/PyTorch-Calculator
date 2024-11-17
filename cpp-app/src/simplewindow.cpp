#include "simplewindow.h"


std::map<std::string, Window> WINDOWS;


// MARK: Initialize()
/**
 * @brief Initialize a window with the specified parameters. The window will not be shown until Show() is called.
 * 
 * @param Name The name identifier for the window.
 * @param Size The size (width, height) of the window. If (0, 0), default values will be used.
 * @param Position The position (x, y) of the window on the screen. If (0, 0), defaults will be used.
 * @param TitleBarColor The RGB color of the window's title bar.
 * @param Resizable If true, the window can be resized.
 * @param TopMost If true, the window will stay on top of other windows.
 * @param Foreground If true, the window will be set to the foreground.
 * @param Minimized If true, the window will be minimized.
 * @param Undestroyable If true, the window will be recreated if closed.
 * @param Icon Path to the icon file for the window. Must be a .ico file.
 * @param NoWarnings If true, no warnings will be printed.
 * @return True if the window was successfully initialized, false otherwise.
 */
bool SimpleWindow::Initialize(std::string Name,
                              std::tuple<int, int> Size,
                              std::tuple<int, int> Position,
                              std::tuple<int, int, int> TitleBarColor,
                              bool Resizable,
                              bool TopMost,
                              bool Foreground,
                              bool Minimized,
                              bool Undestroyable,
                              std::string Icon,
                              bool NoWarnings) {

        HWND HWND = FindWindowW(NULL, std::wstring(Name.begin(), Name.end()).c_str());
        if (HWND != NULL) {
            if (NoWarnings != true) {
                std::cout << Variables::RED << "The window '" << Name << "' already exists, not creating a new window. (" << Name << ": " << HWND << ")" << Variables::NORMAL << std::endl;
            }
            return false;

        WINDOWS[Name] = Window();
        WINDOWS[Name].SetName(Name);
        WINDOWS[Name].SetSize(Size);
        WINDOWS[Name].SetPosition(Position);
        WINDOWS[Name].SetTitleBarColor(TitleBarColor);
        WINDOWS[Name].SetResizable(Resizable);
        WINDOWS[Name].SetTopMost(TopMost);
        WINDOWS[Name].SetForeground(Foreground);
        WINDOWS[Name].SetMinimized(Minimized);
        WINDOWS[Name].SetUndestroyable(Undestroyable);
        WINDOWS[Name].SetIcon(Icon);
        WINDOWS[Name].SetNoWarnings(NoWarnings);

        return true;
    }
}


// MARK: Create()
/**
 * @brief Creates a window based on the parameters specified in Initialize(). This function is not meant to be called manually. It is called internally by Show() or SetOpen().
 * 
 * @param Name The name identifier for the window.
 */
void SimpleWindow::Create(std::string Name) {
    std::tuple<int, int> Size = WINDOWS[Name].GetSize();
    std::tuple<int, int> Position = WINDOWS[Name].GetPosition();
    std::tuple<int, int, int> TitleBarColor = WINDOWS[Name].GetTitleBarColor();
    bool Resizable = WINDOWS[Name].GetResizable();
    bool TopMost = WINDOWS[Name].GetTopMost();
    bool Foreground = WINDOWS[Name].GetForeground();
    bool Minimized = WINDOWS[Name].GetMinimized();
    std::string Icon = WINDOWS[Name].GetIcon();

    if (std::get<0>(Size) == INT_MIN) {
        Size = std::make_tuple(150, std::get<1>(Size));
    }
    if (std::get<1>(Size) == INT_MIN) {
        Size = std::make_tuple(std::get<0>(Size), 150);
    }

    if (std::get<0>(Position) == INT_MIN) {
        Position = std::make_tuple(0, std::get<1>(Position));
    }
    if (std::get<1>(Position) == INT_MIN) {
        Position = std::make_tuple(std::get<0>(Position), 0);
    }

    WINDOWS[Name].SetSize(Size);
    WINDOWS[Name].SetPosition(Position);


    HWND HWND = FindWindowW(NULL, std::wstring(Name.begin(), Name.end()).c_str());
	std::uint32_t ConvertedTitleBarColor = (std::get<0>(TitleBarColor) << 16) | (std::get<1>(TitleBarColor) << 8) | std::get<2>(TitleBarColor);
	DwmSetWindowAttribute(HWND, DWMWA_CAPTION_COLOR, &ConvertedTitleBarColor, sizeof(ConvertedTitleBarColor));

    std::replace(Icon.begin(), Icon.end(), '\\', '/');
    if (std::filesystem::exists(Icon) && Icon.substr(Icon.length() - 4) == ".ico") {
        HICON IconHandle = static_cast<HICON>(LoadImageA(nullptr, Icon.c_str(), IMAGE_ICON, 0, 0, LR_LOADFROMFILE | LR_DEFAULTSIZE));
        SendMessageA(HWND, WM_SETICON, ICON_SMALL, reinterpret_cast<LPARAM>(IconHandle));
        SendMessageA(HWND, WM_SETICON, ICON_BIG, reinterpret_cast<LPARAM>(IconHandle));
    }

    // TODO: Continue with translation!

}