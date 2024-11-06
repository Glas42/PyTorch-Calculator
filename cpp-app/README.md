# PyTorch-Calculator C++

### About

My goal is to recreate the Python PyTorch-Calculator app in C++, i never used C++ before so the code might not be good.

### Build

- Get [LibTorch](https://pytorch.org/)
  - Unzip it
  - Create an environment variable named `LIBTORCH` and set its value to the path of the LibTorch folder, which contains folders like `lib`, `bin`, `include`, etc.
- Get [CMake](https://cmake.org/)
  - Install it (select the option to add it to the system PATH)
  - Open a terminal and cd into the `cpp-app` folder
  - Run ```cmake --preset=x64-release -B build/x64-release && cmake --build build/x64-release``` to build the app
  - Run ```.\build\x64-release\Debug\cpp-app.exe``` to run the app