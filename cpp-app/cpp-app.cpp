#include <iostream>
#include "src/analyze.h"
#include "src/canvas.h"
#include "src/console.h"
#include "src/crashreport.h"
#include "src/file.h"
#include "src/keyboard.h"
#include "src/mouse.h"
#include "src/pytorch.h"
#include "src/settings.h"
#include "src/translate.h"
#include "src/ui.h"
#include "src/updater.h"

int main()
{
    std::cout << "Calling the functions!\n";
    Analyze();
    Canvas();
	Console();
	CrashReport();
	File();
	Keyboard();
	Mouse();
	PyTorch();
	Settings();
	Translate();
	UI();
	Updater();
    std::cout << "Called the functions!";
	return 0;
}