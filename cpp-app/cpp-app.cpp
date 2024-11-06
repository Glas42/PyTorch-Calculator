#include "cpp-app.h"

int main() {
	PyTorchExampleTensor();

	#ifdef BUILD_TYPE_DEBUG
		int ConsoleWidth = 80;
		CONSOLE_SCREEN_BUFFER_INFO csbi;
		if (GetConsoleScreenBufferInfo(GetStdHandle(STD_OUTPUT_HANDLE), &csbi)) {
			ConsoleWidth = csbi.srWindow.Right - csbi.srWindow.Left + 1;
		}
		std::cout << "\n" << std::string(ConsoleWidth, '-') << std::endl;
	#elif defined(BUILD_TYPE_RELEASE)
		std::cout << std::endl;
		system("pause");
	#endif
}