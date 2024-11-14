#include "cpp-app.h"

int main() {
	if (std::filesystem::exists(PATH + "cache") == false) {
		std::filesystem::create_directory(PATH + "cache");
	}

	UI::Initialize();

	std::cout << "Close the window to continue!" << std::endl;

	cv::Mat Frame = OpenCV::EmptyImage(500, 200, 3, 0, 0, 0);
	OpenCV::ShowImage("Close the window to continue!", Frame, false);
	OpenCV::SetWindowCaptionColor(L"Close the window to continue!", 0, 0, 0);
	OpenCV::SetWindowBorderColor(L"Close the window to continue!", 200, 0, 0);
	OpenCV::ShowImage("Close the window to continue!", Frame, true);

	PyTorch::LoadExampleModel();

	PyTorch::ExampleTensor();
	PyTorch::Initialize("Glas42", "PyTorch-Calculator", true);
	PyTorch::Loaded("PyTorch-Calculator");


	if (BUILD_TYPE == "Release") {
		system("pause");
	}
}