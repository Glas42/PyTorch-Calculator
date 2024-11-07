#include "variables.h"

// This needs to be here for some reason
#define WIN32_LEAN_AND_MEAN
#define VC_EXTRALEAN
#include <Windows.h>

std::string GetExePath() {
    std::string PATH = "";
    wchar_t wc[260] = {0};
    GetModuleFileNameW(NULL, wc, 260);
    std::wstring ws(wc);
    transform(ws.begin(), ws.end(), back_inserter(PATH), [](wchar_t c) { return (char)c; });
    return PATH.substr(0, PATH.rfind("\\") + 1);
}

std::string PATH = GetExePath();

#ifdef BUILD_TYPE_RELEASE
    std::string BUILD_TYPE = "Release";
#elif defined(BUILD_TYPE_DEBUG)
    std::string BUILD_TYPE = "Debug";
#endif