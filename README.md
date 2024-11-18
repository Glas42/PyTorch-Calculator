# PyTorch-Calculator


### About

What is this app?
PyTorch-Calculator is a python application that uses a custom PyTorch ML model to interpret and solve mathematical expressions you've drawn to the UI.
The machine learning model and the dataset used for training are available on [Hugging Face](https://huggingface.co/Glas42/PyTorch-Calculator). The app will automatically download and update the model as needed.
The app has only been tested on Windows and is also probably not compatible with other platforms.


### How to Install the app

1. Download Python 3.11.x from [here](https://www.python.org/downloads/windows/) and install it
2. Clone or [download](https://github.com/Glas42/PyTorch-Calculator/archive/refs/heads/main.zip) this repository
3. Run the ```Start.bat``` script, it will automatically create a virtual environment and install the required packages

- The build instructions for the C++ version can be found [here](https://github.com/Glas42/PyTorch-Calculator/tree/main/cpp-app#readme)


### What is the current state of the app?

The app is currently being rewritten in C++ to improve performance, but the Python version works fine. The current detection model works but it's not perfect and only detects the following characters: `0, 1, 2, 3, 4, 5, 6, 7, 8, 9, +, -, *, /, =, (, )`.

![Preview](https://github.com/Glas42/PyTorch-Calculator/blob/main/app/assets/Preview.png)