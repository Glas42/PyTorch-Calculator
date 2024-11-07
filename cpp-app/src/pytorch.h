#ifndef PYTORCH_H
#define PYTORCH_H

#include "variables.h"

#include <torch/torch.h>
#include <unordered_map>
#include <exception>
#include <iostream>
#include <string>

class PyTorch {
    public:
    static void ExampleTensor();
    static void Initialize(std::string Owner = "", std::string Model = "", bool Threaded = true);
};

#endif