#include "simplewindow.h"

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
bool Initialize(std::string Name = "",
    std::tuple<int, int> Size = std::make_tuple(0, 0),
    std::tuple<int, int> Position = std::make_tuple(0, 0),
    std::tuple<int, int, int> TitleBarColor = std::make_tuple(0, 0, 0),
    bool Resizable = true,
    bool TopMost = false,
    bool Foreground = true,
    bool Minimized = false,
    bool Undestroyable = false,
    std::string Icon = "",
    bool NoWarnings = false) {

        HWND HWND = FindWindowW(NULL, std::wstring(Name.begin(), Name.end()).c_str());
        if (HWND != NULL) {
            if (NoWarnings != true) {
                std::cout << RED << "The window '" << Name << "' already exists, not creating a new window. (" << Name << ": " << HWND << ")" << NORMAL << std::endl;
            }
            return false;



        return true;
    }
}