#ifndef PYTORCH_H
#define PYTORCH_H

#include "variables.h"

#include <torch/torch.h>
#include <unordered_map>
#include <exception>
#include <iostream>
#include <string>

extern std::map<std::string, std::map<std::string, std::string>> MODELS;

void PyTorchExampleTensor();

void PyTorchInitialize(std::string Owner = "", std::string Model = "", bool Threaded = true);

#endif