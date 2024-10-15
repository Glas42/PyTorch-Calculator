#include <windows.h>
#include <dwmapi.h>

LRESULT CALLBACK WndProc(HWND, UINT, WPARAM, LPARAM);

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow)
{
    WNDCLASS wc = { 0 };
    wc.lpfnWndProc = WndProc;
    wc.hInstance = hInstance;
    wc.hCursor = LoadCursor(NULL, IDC_ARROW);
    wc.hbrBackground = (HBRUSH)CreateSolidBrush(RGB(28, 28, 28));
    wc.lpszClassName = L"WindowClass";

    RegisterClass(&wc);
    HWND hWnd = CreateWindowEx(0, L"WindowClass", L"PyTorch-Calculator", WS_OVERLAPPEDWINDOW, CW_USEDEFAULT, CW_USEDEFAULT, CW_USEDEFAULT, CW_USEDEFAULT, NULL, NULL, hInstance, NULL);
    if (hWnd == NULL)
    {
        return 0;
    }

    COLORREF color = RGB(28, 28, 28);
    DwmSetWindowAttribute(hWnd, DWMWINDOWATTRIBUTE::DWMWA_CAPTION_COLOR, &color, sizeof(color));

    ShowWindow(hWnd, nCmdShow);
    MSG msg = { 0 };
    while (GetMessage(&msg, NULL, 0, 0))
    {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }
    return 0;
}

LRESULT CALLBACK WndProc(HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam)
{
    static HWND hLabel;
    static HWND hButton;

    switch (message)
    {
    case WM_CREATE:
        // Create a static control (label)
        hLabel = CreateWindow(
            L"STATIC",
            L"PyTorch-Calculator",
            WS_VISIBLE | WS_CHILD | SS_CENTER,
            50, 50, 200, 20,
            hWnd,
            NULL,
            (HINSTANCE)GetWindowLongPtr(hWnd, GWLP_HINSTANCE),
            NULL);


        hButton = CreateWindow(
            L"BUTTON",
            L"Exit",
            WS_VISIBLE | WS_CHILD | BS_DEFPUSHBUTTON,
            50, 100, 200, 20,
            hWnd,
            NULL,
            (HINSTANCE)GetWindowLongPtr(hWnd, GWLP_HINSTANCE),
            NULL
        );

		SendMessage(hButton, WM_SETFONT, (WPARAM)GetStockObject(DEFAULT_GUI_FONT), TRUE);

        SendMessage(hLabel, WM_SETFONT, (WPARAM)GetStockObject(DEFAULT_GUI_FONT), TRUE);
        break;

    case WM_DESTROY:
        PostQuitMessage(0);
        break;

    default:
        return DefWindowProc(hWnd, message, wParam, lParam);
    }
    return 0;
}