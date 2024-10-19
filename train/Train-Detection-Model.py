import datetime
print(f"\n----------------------------------------------\n\n\033[90m[{datetime.datetime.now().strftime('%H:%M:%S')}] \033[0mImporting libraries...")

import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

from torch.utils.tensorboard import SummaryWriter
from torch.utils.data import Dataset, DataLoader
import torch.optim.lr_scheduler as lr_scheduler
from torch.amp import GradScaler, autocast
from torchvision import transforms
from PIL import Image as PILImage
import torch.optim as optim
import multiprocessing
import torch.nn as nn
import numpy as np
import threading
import random
import shutil
import torch
import time
import cv2

PATH = os.path.dirname(__file__).replace("\\", "/") + ("/" if os.path.dirname(__file__).replace("\\", "/")[-1] != "/" else "")
DATA_PATH = PATH + "dataset/final/"
MODEL_PATH = PATH + "models/"
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
NUM_EPOCHS = 500
BATCH_SIZE = 100
IMG_WIDTH = 50
IMG_HEIGHT = 50
LEARNING_RATE = 0.001
MAX_LEARNING_RATE = 0.001
TRAIN_VAL_RATIO = 0.8
NUM_WORKERS = 0
DROPOUT = 0.3
PATIENCE = -1
SHUFFLE = True
PIN_MEMORY = False
DROP_LAST = True
CACHE = True

IMG_COUNT = 0
for File in os.listdir(DATA_PATH):
    if File.endswith(".png"):
        IMG_COUNT += 1
if IMG_COUNT == 0:
    print("No images found, exiting...")
    exit()

CLASSES = []
for File in os.listdir(DATA_PATH):
    if File.endswith(".txt"):
        with open(DATA_PATH + File, "r") as F:
            Class = F.read()
            if Class not in CLASSES:
                CLASSES.append(Class)
CLASSLIST = sorted(CLASSES)
CLASSES = len(CLASSES)
if CLASSES == 0:
    print("No classes found, exiting...")
    exit()

RED = "\033[91m"
GREEN = "\033[92m"
DARK_GREY = "\033[90m"
NORMAL = "\033[0m"
def timestamp():
    return DARK_GREY + f"[{datetime.datetime.now().strftime('%H:%M:%S')}] " + NORMAL

print("\n----------------------------------------------\n")

print(timestamp() + f"Using {str(DEVICE).upper()} for training")
print(timestamp() + 'Number of CPU cores:', multiprocessing.cpu_count())
print()
print(timestamp() + "Training settings:")
print(timestamp() + "> Epochs:", NUM_EPOCHS)
print(timestamp() + "> Batch size:", BATCH_SIZE)
print(timestamp() + "> Classes:", CLASSES)
print(timestamp() + "> Images:", IMG_COUNT)
print(timestamp() + "> Image width:", IMG_WIDTH)
print(timestamp() + "> Image height:", IMG_HEIGHT)
print(timestamp() + "> Learning rate:", LEARNING_RATE)
print(timestamp() + "> Max learning rate:", MAX_LEARNING_RATE)
print(timestamp() + "> Dataset split:", TRAIN_VAL_RATIO)
print(timestamp() + "> Number of workers:", NUM_WORKERS)
print(timestamp() + "> Dropout:", DROPOUT)
print(timestamp() + "> Patience:", PATIENCE)
print(timestamp() + "> Shuffle:", SHUFFLE)
print(timestamp() + "> Pin memory:", PIN_MEMORY)
print(timestamp() + "> Drop last:", DROP_LAST)
print(timestamp() + "> Cache:", CACHE)


if CACHE:
    def LoadData(Files=None, Type=None):
        Images = []
        Labels = []
        print(f"\r{timestamp()}Caching {Type} dataset...           ", end='', flush=True)
        for File in os.listdir(DATA_PATH):
            if File in Files:
                Image = PILImage.open(os.path.join(DATA_PATH, File)).convert('L')
                Image = np.array(Image)

                Image = cv2.resize(Image, (IMG_WIDTH, IMG_HEIGHT))
                Image = Image / 255.0

                LabelsFile = os.path.join(DATA_PATH, File.replace(File.split(".")[-1], "txt"))
                if os.path.exists(LabelsFile):
                    with open(LabelsFile, 'r') as F:
                        Content = str(F.read())
                        Label = [0] * CLASSES
                        Label[CLASSLIST.index(Content)] = 1
                    Images.append(Image)
                    Labels.append(Label)

            if len(Images) % (round(len(Files) / 100) if round(len(Files) / 100) > 0 else 1) == 0:
                print(f"\r{timestamp()}Caching {Type} dataset... ({round(100 * len(Images) / len(Files))}%)", end='', flush=True)

        return np.array(Images, dtype=np.float32), np.array(Labels, dtype=np.float32)

    class CustomDataset(Dataset):
        def __init__(self, Images, Labels, Transform=None):
            self.Images = Images
            self.Labels = Labels
            self.Transform = Transform

        def __len__(self):
            return len(self.Images)

        def __getitem__(self, idx):
            Image = self.Images[idx]
            Label = self.Labels[idx]
            Image = self.Transform(Image)
            return Image, torch.as_tensor(Label, dtype=torch.float32)

else:

    class CustomDataset(Dataset):
        def __init__(self, files=None, Transform=None):
            self.files = files
            self.Transform = Transform

        def __len__(self):
            return len(self.files)

        def __getitem__(self, index):
            ImageName = self.files[index]
            ImagePath = os.path.join(DATA_PATH, ImageName)
            LabelPath = os.path.join(DATA_PATH, ImageName.replace(ImageName.split('.')[-1], 'txt'))

            Image = PILImage.open(ImagePath).convert('L')
            Image = np.array(Image)

            Image = cv2.resize(Image, (IMG_WIDTH, IMG_HEIGHT))
            Image = Image / 255.0

            with open(LabelPath, 'r') as F:
                Content = str(F.read())
                Label = [0] * CLASSES
                Label[CLASSLIST.index(Content)] = 1

            Image = np.array(Image, dtype=np.float32)
            Image = self.Transform(Image)
            return Image, torch.as_tensor(Label, dtype=torch.float32)


class ConvolutionalNeuralNetwork(nn.Module):
    def __init__(self):
        super(ConvolutionalNeuralNetwork, self).__init__()
        self.conv2d_1 = nn.Conv2d(1, 32, (3, 3), padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(32)
        self.relu_1 = nn.ReLU()
        self.maxpool_1 = nn.MaxPool2d((2, 2))

        self.conv2d_2 = nn.Conv2d(32, 64, (3, 3), padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(64)
        self.relu_2 = nn.ReLU()
        self.maxpool_2 = nn.MaxPool2d((2, 2))

        self.conv2d_3 = nn.Conv2d(64, 128, (3, 3), padding=1, bias=False)
        self.bn3 = nn.BatchNorm2d(128)
        self.relu_3 = nn.ReLU()
        self.maxpool_3 = nn.MaxPool2d((2, 2))

        self.flatten = nn.Flatten()
        self.dropout = nn.Dropout(DROPOUT)
        self.linear_1 = nn.Linear(128 * (IMG_WIDTH // 8) * (IMG_HEIGHT // 8), 256, bias=False)
        self.bn4 = nn.BatchNorm1d(256)
        self.relu_4 = nn.ReLU()
        self.linear_2 = nn.Linear(256, CLASSES, bias=False)
        self.softmax = nn.Softmax(dim=1)

    def forward(self, x):
        x = self.conv2d_1(x)
        x = self.bn1(x)
        x = self.relu_1(x)
        x = self.maxpool_1(x)

        x = self.conv2d_2(x)
        x = self.bn2(x)
        x = self.relu_2(x)
        x = self.maxpool_2(x)

        x = self.conv2d_3(x)
        x = self.bn3(x)
        x = self.relu_3(x)
        x = self.maxpool_3(x)

        x = self.flatten(x)
        x = self.dropout(x)
        x = self.linear_1(x)
        x = self.bn4(x)
        x = self.relu_4(x)
        x = self.linear_2(x)
        x = self.softmax(x)
        return x


def main():
    Model = ConvolutionalNeuralNetwork().to(DEVICE)

    def GetModelSizeMB(Model):
        TotalParams = 0
        for Param in Model.parameters():
            TotalParams += np.prod(Param.size())
        TrainableParams = sum(p.numel() for p in Model.parameters() if p.requires_grad)
        NonTrainableParams = TotalParams - TrainableParams
        BytesPerParam = next(Model.parameters()).element_size()
        ModelSizeMb = (TotalParams * BytesPerParam) / (1024 ** 2)
        return TotalParams, TrainableParams, NonTrainableParams, ModelSizeMb

    TotalParams, TrainableParams, NonTrainableParams, ModelSizeMb = GetModelSizeMB(Model)

    print()
    print(timestamp() + "Model properties:")
    print(timestamp() + f"> Total parameters: {TotalParams}")
    print(timestamp() + f"> Trainable parameters: {TrainableParams}")
    print(timestamp() + f"> Non-trainable parameters: {NonTrainableParams}")
    print(timestamp() + f"> Predicted model size: {ModelSizeMb:.2f}MB")

    print("\n----------------------------------------------\n")

    print(timestamp() + "Loading...")

    if not os.path.exists(f"{PATH}tensorboard"):
        os.makedirs(f"{PATH}tensorboard")

    for OBJ in os.listdir(f"{PATH}tensorboard"):
        try:
            shutil.rmtree(f"{PATH}tensorboard/{OBJ}")
        except:
            os.remove(f"{PATH}tensorboard/{OBJ}")

    Summary = SummaryWriter(f"{PATH}tensorboard", comment="Train-Detection-Model", flush_secs=20)

    TrainTransform = transforms.Compose([
        transforms.ToTensor(),
        transforms.RandomRotation(10),
        transforms.RandomCrop((round(IMG_HEIGHT * random.uniform(0.5, 1)), round(IMG_WIDTH * random.uniform(0.5, 1)))),
        transforms.Resize((IMG_HEIGHT, IMG_WIDTH))
    ])

    ValTransform = transforms.Compose([
        transforms.ToTensor()
    ])

    AllFiles = [F for F in os.listdir(DATA_PATH) if F.endswith(".png") and os.path.exists(F"{DATA_PATH}{F.replace(F.split('.')[-1], 'txt')}")]
    random.shuffle(AllFiles)
    TrainSize = int(len(AllFiles) * TRAIN_VAL_RATIO)
    ValSize = len(AllFiles) - TrainSize
    TrainFiles = AllFiles[:TrainSize]
    ValFiles = AllFiles[TrainSize:]

    if CACHE:
        TrainImages, TrainLabels = LoadData(TrainFiles, "train")
        ValImages, ValLabels = LoadData(ValFiles, "val")
        TrainDataset = CustomDataset(TrainImages, TrainLabels, Transform=TrainTransform)
        ValDataset = CustomDataset(ValImages, ValLabels, Transform=ValTransform)
    else:
        TrainDataset = CustomDataset(TrainFiles, Transform=TrainTransform)
        ValDataset = CustomDataset(ValFiles, Transform=ValTransform)

    TrainDataLoader = DataLoader(TrainDataset, batch_size=BATCH_SIZE, shuffle=SHUFFLE, num_workers=NUM_WORKERS, pin_memory=PIN_MEMORY, drop_last=DROP_LAST)
    ValDataLoader = DataLoader(ValDataset, batch_size=BATCH_SIZE, shuffle=SHUFFLE, num_workers=NUM_WORKERS, pin_memory=PIN_MEMORY)

    Scaler = GradScaler(device=str(DEVICE))
    Criterion = nn.CrossEntropyLoss()
    Optimizer = optim.Adam(Model.parameters(), lr=LEARNING_RATE)
    Scheduler = lr_scheduler.OneCycleLR(Optimizer, max_lr=MAX_LEARNING_RATE, steps_per_epoch=len(TrainDataLoader), epochs=NUM_EPOCHS)

    BestValidationLoss = float('inf')
    BestModel = None
    BestModelEpoch = None
    BestModelTrainingLoss = None
    BestModelValidationLoss = None
    Wait = 0

    print(f"\r{timestamp()}Starting training...                ")
    print("\n-----------------------------------------------------------------------------------------------------------\n")

    TrainingTimePrediction = time.time()
    TrainingStartTime = time.time()
    EpochTotalTime = 0
    TrainingLoss = 0
    ValidationLoss = 0
    TrainingEpoch = 0

    global PROGRESS_PRINT
    PROGRESS_PRINT = "initializing"
    def TrainingProgressPrint():
        global PROGRESS_PRINT
        def NumToStr(Num: int):
            StrNum = format(Num, '.15f')
            while len(StrNum) > 15:
                StrNum = StrNum[:-1]
            while len(StrNum) < 15:
                StrNum = StrNum + '0'
            return StrNum
        while PROGRESS_PRINT == "initializing":
            time.sleep(1)
        LastMessage = ""
        while PROGRESS_PRINT == "running":
            Progress = (time.time() - EpochTotalStartTime) / EpochTotalTime
            if Progress > 1: Progress = 1
            if Progress < 0: Progress = 0
            Progress = '█' * round(Progress * 10) + '░' * (10 - round(Progress * 10))
            EpochTime = round(EpochTotalTime, 2) if EpochTotalTime > 1 else round((EpochTotalTime) * 1000)
            ETA = time.strftime('%H:%M:%S', time.gmtime(round((TrainingTimePrediction - TrainingStartTime) / (TrainingEpoch) * NUM_EPOCHS - (TrainingTimePrediction - TrainingStartTime) + (TrainingTimePrediction - time.time()), 2)))
            Message = f"{Progress} Epoch {TrainingEpoch}, Train Loss: {NumToStr(TrainingLoss)}, Val Loss: {NumToStr(ValidationLoss)}, {EpochTime}{'s' if EpochTotalTime > 1 else 'ms'}/Epoch, ETA: {ETA}"
            print(f"\r{Message}" + (" " * (len(LastMessage) - len(Message)) if len(LastMessage) > len(Message) else ""), end='', flush=True)
            LastMessage = Message
            time.sleep(1)
        if PROGRESS_PRINT == "early stopped":
            Message = f"Early stopping at Epoch {TrainingEpoch}, Train Loss: {NumToStr(TrainingLoss)}, Val Loss: {NumToStr(ValidationLoss)}"
            print(f"\r{Message}" + (" " * (len(LastMessage) - len(Message)) if len(LastMessage) > len(Message) else ""), end='', flush=True)
        elif PROGRESS_PRINT == "finished":
            Message = f"Finished at Epoch {TrainingEpoch}, Train Loss: {NumToStr(TrainingLoss)}, Val Loss: {NumToStr(ValidationLoss)}"
            print(f"\r{Message}" + (" " * (len(LastMessage) - len(Message)) if len(LastMessage) > len(Message) else ""), end='', flush=True)
        PROGRESS_PRINT = "received"
    threading.Thread(target=TrainingProgressPrint, daemon=True).start()

    for Epoch, _ in enumerate(range(NUM_EPOCHS), 1):
        EpochTotalStartTime = time.time()


        EpochTrainingStartTime = time.time()

        Model.train()
        RunningTrainingLoss = 0.0
        for i, Data in enumerate(TrainDataLoader, 0):
            Inputs, Labels = Data[0].to(DEVICE, non_blocking=True), Data[1].to(DEVICE, non_blocking=True)
            Optimizer.zero_grad()
            with autocast(device_type=str(DEVICE)):
                Outputs = Model(Inputs)
                Loss = Criterion(Outputs, Labels)
            Scaler.scale(Loss).backward()
            Scaler.step(Optimizer)
            Scaler.update()
            Scheduler.step()
            RunningTrainingLoss += Loss.item()
        RunningTrainingLoss /= len(TrainDataLoader)
        TrainingLoss = RunningTrainingLoss

        EpochTrainingTime = time.time() - EpochTrainingStartTime


        EpochValidationStartTime = time.time()

        Model.eval()
        RunningValidationLoss = 0.0
        with torch.no_grad(), autocast(device_type=str(DEVICE)):
            for i, Data in enumerate(ValDataLoader, 0):
                Inputs, Labels = Data[0].to(DEVICE, non_blocking=True), Data[1].to(DEVICE, non_blocking=True)
                Outputs = Model(Inputs)
                Loss = Criterion(Outputs, Labels)
                RunningValidationLoss += Loss.item()
        RunningValidationLoss /= len(ValDataLoader)
        ValidationLoss = RunningValidationLoss

        EpochValidationTime = time.time() - EpochValidationStartTime


        if ValidationLoss < BestValidationLoss:
            BestValidationLoss = ValidationLoss
            BestModel = Model
            BestModelEpoch = Epoch
            BestModelTrainingLoss = TrainingLoss
            BestModelValidationLoss = ValidationLoss
            Wait = 0
        else:
            Wait += 1
            if Wait >= PATIENCE and PATIENCE > 0:
                EpochTotalTime = time.time() - EpochTotalStartTime
                Summary.add_scalars('Stats', {
                    'TrainLoss': TrainingLoss,
                    'ValidationLoss': ValidationLoss,
                    'EpochTotalTime': EpochTotalTime,
                    'EpochTrainingTime': EpochTrainingTime,
                    'EpochValidationTime': EpochValidationTime
                }, Epoch)
                TrainingTimePrediction = time.time()
                PROGRESS_PRINT = "early stopped"
                break

        EpochTotalTime = time.time() - EpochTotalStartTime

        Summary.add_scalars('Stats', {
            'TrainLoss': TrainingLoss,
            'ValidationLoss': ValidationLoss,
            'EpochTotalTime': EpochTotalTime,
            'EpochTrainingTime': EpochTrainingTime,
            'EpochValidationTime': EpochValidationTime
        }, Epoch)
        TrainingEpoch = Epoch
        TrainingTimePrediction = time.time()
        PROGRESS_PRINT = "running"

    if PROGRESS_PRINT != "early stopped":
        PROGRESS_PRINT = "finished"
    while PROGRESS_PRINT != "received":
        time.sleep(1)

    print("\n\n-----------------------------------------------------------------------------------------------------------")

    TRAINING_TIME = time.strftime('%H-%M-%S', time.gmtime(time.time() - TrainingStartTime))
    TRAINING_DATE = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

    print()
    print(timestamp() + "Training completed after " + TRAINING_TIME.replace('-', ':'))

    print(timestamp() + "Saving the last model...")

    torch.cuda.empty_cache()

    Model.eval()
    TotalTrain = 0
    CorrectTrain = 0
    with torch.no_grad():
        for Data in TrainDataLoader:
            Images, Labels = Data
            Images, Labels = Images.to(DEVICE), Labels.to(DEVICE)
            Outputs = Model(Images)
            _, Predicted = torch.max(Outputs.data, 1)
            TotalTrain += Labels.size(0)
            CorrectTrain += (Predicted == torch.argmax(Labels, dim=1)).sum().item()
    TrainingDatasetAccuracy = str(round(100 * (CorrectTrain / TotalTrain), 2)) + "%"

    torch.cuda.empty_cache()

    TotalVal = 0
    CorrectVal = 0
    with torch.no_grad():
        for Data in ValDataLoader:
            Images, Labels = Data
            Images, Labels = Images.to(DEVICE), Labels.to(DEVICE)
            Outputs = Model(Images)
            _, Predicted = torch.max(Outputs.data, 1)
            TotalVal += Labels.size(0)
            CorrectVal += (Predicted == torch.argmax(Labels, dim=1)).sum().item()
    ValidationDatasetAccuracy = str(round(100 * (CorrectVal / TotalVal), 2)) + "%"

    MetadataOptimizer = str(Optimizer).replace('\n', '')
    MetadataCriterion = str(Criterion).replace('\n', '')
    MetadataModel = str(Model).replace('\n', '')
    Metadata = (f"epochs#{Epoch}",
                f"batch#{BATCH_SIZE}",
                f"classes#{CLASSES}",
                f"outputs#{CLASSES}",
                f"class_list#{CLASSLIST}",
                f"image_count#{IMG_COUNT}",
                f"image_width#{IMG_WIDTH}",
                f"image_height#{IMG_HEIGHT}",
                f"learning_rate#{LEARNING_RATE}",
                f"max_learning_rate#{MAX_LEARNING_RATE}",
                f"dataset_split#{TRAIN_VAL_RATIO}",
                f"number_of_workers#{NUM_WORKERS}",
                f"dropout#{DROPOUT}",
                f"patience#{PATIENCE}",
                f"shuffle#{SHUFFLE}",
                f"pin_memory#{PIN_MEMORY}",
                f"training_time#{TRAINING_TIME}",
                f"training_date#{TRAINING_DATE}",
                f"training_device#{DEVICE}",
                f"training_os#{os.name}",
                f"architecture#{MetadataModel}",
                f"torch_version#{torch.__version__}",
                f"numpy_version#{np.__version__}",
                f"pil_version#{PILImage.__version__}",
                f"train_transform#{TrainTransform}",
                f"val_transform#{ValTransform}",
                f"optimizer#{MetadataOptimizer}",
                f"loss_function#{MetadataCriterion}",
                f"training_size#{TrainSize}",
                f"validation_size#{ValSize}",
                f"training_loss#{BestModelTrainingLoss}",
                f"validation_loss#{BestModelValidationLoss}",
                f"training_dataset_accuracy#{TrainingDatasetAccuracy}",
                f"validation_dataset_accuracy#{ValidationDatasetAccuracy}")
    Metadata = {"data": Metadata}
    Metadata = {Data: str(Value).encode("ascii") for Data, Value in Metadata.items()}

    LastModelSaved = False
    for i in range(5):
        try:
            LastModel = torch.jit.script(Model)
            torch.jit.save(LastModel, os.path.join(MODEL_PATH, f"DetectionModel-LAST-{TRAINING_DATE}.pt"), _extra_files=Metadata)
            LastModelSaved = True
            break
        except:
            print(timestamp() + "Failed to save the last model. Retrying...")
    print(timestamp() + "Last model saved successfully.") if LastModelSaved else print(timestamp() + "Failed to save the last model.")

    print(timestamp() + "Saving the best model...")

    torch.cuda.empty_cache()

    BestModel.eval()
    TotalTrain = 0
    CorrectTrain = 0
    with torch.no_grad():
        for Data in TrainDataLoader:
            Images, Labels = Data
            Images, Labels = Images.to(DEVICE), Labels.to(DEVICE)
            Outputs = BestModel(Images)
            _, Predicted = torch.max(Outputs.data, 1)
            TotalTrain += Labels.size(0)
            CorrectTrain += (Predicted == torch.argmax(Labels, dim=1)).sum().item()
    TrainingDatasetAccuracy = str(round(100 * (CorrectTrain / TotalTrain), 2)) + "%"

    torch.cuda.empty_cache()

    TotalVal = 0
    CorrectVal = 0
    with torch.no_grad():
        for Data in ValDataLoader:
            Images, Labels = Data
            Images, Labels = Images.to(DEVICE), Labels.to(DEVICE)
            Outputs = BestModel(Images)
            _, Predicted = torch.max(Outputs.data, 1)
            TotalVal += Labels.size(0)
            CorrectVal += (Predicted == torch.argmax(Labels, dim=1)).sum().item()
    ValidationDatasetAccuracy = str(round(100 * (CorrectVal / TotalVal), 2)) + "%"

    MetadataOptimizer = str(Optimizer).replace('\n', '')
    MetadataCriterion = str(Criterion).replace('\n', '')
    MetadataModel = str(BestModel).replace('\n', '')
    Metadata = (f"epochs#{BestModelEpoch}",
                f"batch#{BATCH_SIZE}",
                f"classes#{CLASSES}",
                f"outputs#{CLASSES}",
                f"class_list#{CLASSLIST}",
                f"image_count#{IMG_COUNT}",
                f"image_width#{IMG_WIDTH}",
                f"image_height#{IMG_HEIGHT}",
                f"learning_rate#{LEARNING_RATE}",
                f"max_learning_rate#{MAX_LEARNING_RATE}",
                f"dataset_split#{TRAIN_VAL_RATIO}",
                f"number_of_workers#{NUM_WORKERS}",
                f"dropout#{DROPOUT}",
                f"patience#{PATIENCE}",
                f"shuffle#{SHUFFLE}",
                f"pin_memory#{PIN_MEMORY}",
                f"training_time#{TRAINING_TIME}",
                f"training_date#{TRAINING_DATE}",
                f"training_device#{DEVICE}",
                f"training_os#{os.name}",
                f"architecture#{MetadataModel}",
                f"torch_version#{torch.__version__}",
                f"numpy_version#{np.__version__}",
                f"pil_version#{PILImage.__version__}",
                f"train_transform#{TrainTransform}",
                f"val_transform#{ValTransform}",
                f"optimizer#{MetadataOptimizer}",
                f"loss_function#{MetadataCriterion}",
                f"training_size#{TrainSize}",
                f"validation_size#{ValSize}",
                f"training_loss#{TrainingLoss}",
                f"validation_loss#{ValidationLoss}",
                f"training_dataset_accuracy#{TrainingDatasetAccuracy}",
                f"validation_dataset_accuracy#{ValidationDatasetAccuracy}")
    Metadata = {"data": Metadata}
    Metadata = {Data: str(Value).encode("ascii") for Data, Value in Metadata.items()}

    BestModelSaved = False
    for i in range(5):
        try:
            BestModel = torch.jit.script(BestModel)
            torch.jit.save(BestModel, os.path.join(MODEL_PATH, f"DetectionModel-BEST-{TRAINING_DATE}.pt"), _extra_files=Metadata)
            BestModelSaved = True
            break
        except:
            print(timestamp() + "Failed to save the best model. Retrying...")
    print(timestamp() + "Best model saved successfully.") if BestModelSaved else print(timestamp() + "Failed to save the best model.")

    print("\n----------------------------------------------\n")

if __name__ == '__main__':
    main()