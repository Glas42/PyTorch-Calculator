#include "pytorch.h"

void PyTorchExampleTensor() {
    torch::Tensor Tensor = torch::rand({3, 3});
    std::cout << "Example of a random tensor:\n" << Tensor << std::endl;
}

//std::unordered_map<std::string, std::unordered_map<std::string, torch::Device>> MODELS;

//void PyTorchInitialize(std::string Owner = "", std::string Model = "", bool Threaded = true) {
//    try {
//        if (torch::cuda::is_available()) {
//            MODELS[Model]["Device"] = "cuda";
//        } else {
//        	MODELS[Model]["Device"] = "cpu";
//        }
//        MODELS[Model]["Path"] = PATH + "cache/" + Model;
//        MODELS[Model]["Threaded"] = Threaded;
//        MODELS[Model]["ModelOwner"] = Owner;
//    }
//    catch (const std::exception& e) {
//        CrashReport("PyTorch - Error in function Initialize.", e.what());
//    }
//}