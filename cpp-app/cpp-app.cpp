#include "cpp-app.h"

int main() {
	if (std::filesystem::exists(PATH + "cache") == false) {
		std::filesystem::create_directory(PATH + "cache");
	}

	UI::Initialize();

	PyTorch::ExampleTensor();
	PyTorch::Initialize("Glas42", "PyTorch-Calculator", true);

	if (BUILD_TYPE == "Release") {
		system("pause");
	}
}