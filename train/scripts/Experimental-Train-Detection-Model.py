import datetime
print(f"\n----------------------------------------------\n\n\033[90m[{datetime.datetime.now().strftime('%H:%M:%S')}] \033[0mImporting libraries...")

import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

from torch.utils.tensorboard import SummaryWriter
from torch.utils.data import Dataset, DataLoader
import torch.optim.lr_scheduler as lr_scheduler
from torch.amp import GradScaler, autocast
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

PATH = os.path.dirname(__file__).replace("\\", "/") + ("/" if os.path.dirname(__file__).replace("\\", "/")[-1] != "/" else "")
DATA_PATH = PATH + "dataset/final/"
MODEL_PATH = PATH + "models/"
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
NUM_EPOCHS = 5000
BATCH_SIZE = 100
LEARNING_RATE = 0.0001
MAX_LEARNING_RATE = 0.0001
TRAIN_VAL_RATIO = 0.8
NUM_WORKERS = 0
DROPOUT = 0.3
PATIENCE = -1
SHUFFLE = True
PIN_MEMORY = False
DROP_LAST = True
CACHE = True

RESOLUTION = 0
OBJECT_COUNT = 0
for File in os.listdir(DATA_PATH):
    if File.endswith(".txt"):
        with open(DATA_PATH + File, "r") as F:
            RESOLUTION = len(eval(str(F.read()).split("###")[1]))
        OBJECT_COUNT += 1
if OBJECT_COUNT == 0:
    print("No objects found, exiting...")
    exit()
elif int(OBJECT_COUNT * TRAIN_VAL_RATIO) < BATCH_SIZE:
    print("Not enough objects for training, exiting...")
    exit()

CLASSES = []
for File in os.listdir(DATA_PATH):
    if File.endswith(".txt"):
        with open(DATA_PATH + File, "r") as F:
            Class = F.read().split("###")[0]
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
print(timestamp() + "> Objects:", OBJECT_COUNT)
print(timestamp() + "> Resolution:", RESOLUTION)
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
        Objects = []
        Labels = []
        print(f"\r{timestamp()}Caching {Type} dataset...           ", end='', flush=True)
        for File in os.listdir(DATA_PATH):
            if File in Files:
                with open(DATA_PATH + File, "r") as F:
                    Content = str(F.read()).split("###")
                    Label = [0] * CLASSES
                    Label[CLASSLIST.index(Content[0])] = 1

                    Object = eval(Content[1])
                    NewObject = []
                    for Point in Object:
                        NewObject.append(Point[0])
                        NewObject.append(Point[1])
                    Object = NewObject

                Labels.append(Label)
                Objects.append(Object)

            if len(Objects) % (round(len(Files) / 100) if round(len(Files) / 100) > 0 else 1) == 0:
                print(f"\r{timestamp()}Caching {Type} dataset... ({(round(100 * len(Objects) / len(Files))) if len(Files) != 0 else 100}%)", end='', flush=True)

        return np.array(Objects, dtype=np.float32), np.array(Labels, dtype=np.float32)

    class CustomDataset(Dataset):
        def __init__(self, Objects, Labels):
            self.Objects = Objects
            self.Labels = Labels

        def __len__(self):
            return len(self.Objects)

        def __getitem__(self, idx):
            Object = self.Objects[idx]
            Label = self.Labels[idx]
            return torch.as_tensor(Object, dtype=torch.float32), torch.as_tensor(Label, dtype=torch.float32)

else:

    class CustomDataset(Dataset):
        def __init__(self, Files=None):
            self.Files = Files

        def __len__(self):
            return len(self.Files)

        def __getitem__(self, Index):
            File = self.Files[Index]
            with open(DATA_PATH + File, "r") as F:
                Content = str(F.read()).split("###")
                Label = [0] * CLASSES
                Label[CLASSLIST.index(Content[0])] = 1

                Object = eval(Content[1])
                NewObject = []
                for Point in Object:
                    NewObject.append(Point[0])
                    NewObject.append(Point[1])
                Object = NewObject

            return torch.as_tensor(Object, dtype=torch.float32), torch.as_tensor(Label, dtype=torch.float32)


class NeuralNetwork(nn.Module):
    def __init__(self):
        super(NeuralNetwork, self).__init__()
        self.linear1 = nn.Linear(2 * RESOLUTION, 32 * RESOLUTION, bias=False)
        self.linear2 = nn.Linear(32 * RESOLUTION, 64 * RESOLUTION, bias=False)
        self.linear3 = nn.Linear(64 * RESOLUTION, 32 * RESOLUTION, bias=False)
        self.linear4 = nn.Linear(32 * RESOLUTION, 2 * RESOLUTION, bias=False)
        self.linear5 = nn.Linear(2 * RESOLUTION, CLASSES, bias=False)
        self.dropout = nn.Dropout(DROPOUT)
        self.softmax = nn.Softmax(dim=1)

    def forward(self, x):
        x = self.linear1(x)
        x = self.linear2(x)
        x = self.linear3(x)
        x = self.linear4(x)
        x = self.linear5(x)
        x = self.dropout(x)
        x = self.softmax(x)
        return x


def main():
    Model = NeuralNetwork().to(DEVICE)

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

    AllFiles = [F for F in os.listdir(DATA_PATH) if F.endswith(".txt")]
    random.shuffle(AllFiles)
    TrainSize = int(len(AllFiles) * TRAIN_VAL_RATIO)
    ValSize = len(AllFiles) - TrainSize
    TrainFiles = AllFiles[:TrainSize]
    ValFiles = AllFiles[TrainSize:]

    if CACHE:
        TrainObjects, TrainLabels = LoadData(TrainFiles, "train")
        ValObjects, ValLabels = LoadData(ValFiles, "val")
        TrainDataset = CustomDataset(TrainObjects, TrainLabels)
        ValDataset = CustomDataset(ValObjects, ValLabels)
    else:
        TrainDataset = CustomDataset(TrainFiles)
        ValDataset = CustomDataset(ValFiles)

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
            Objects, Labels = Data
            Objects, Labels = Objects.to(DEVICE), Labels.to(DEVICE)
            Outputs = Model(Objects)
            _, Predicted = torch.max(Outputs.data, 1)
            TotalTrain += Labels.size(0)
            CorrectTrain += (Predicted == torch.argmax(Labels, dim=1)).sum().item()
    TrainingDatasetAccuracy = str(round(100 * (CorrectTrain / TotalTrain), 2)) + "%"

    torch.cuda.empty_cache()

    TotalVal = 0
    CorrectVal = 0
    with torch.no_grad():
        for Data in ValDataLoader:
            Objects, Labels = Data
            Objects, Labels = Objects.to(DEVICE), Labels.to(DEVICE)
            Outputs = Model(Objects)
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
                f"object_count#{OBJECT_COUNT}",
                f"resolution#{RESOLUTION}",
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
            if os.path.exists(MODEL_PATH) == False:
                os.makedirs(MODEL_PATH)
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
            Objects, Labels = Data
            Objects, Labels = Objects.to(DEVICE), Labels.to(DEVICE)
            Outputs = BestModel(Objects)
            _, Predicted = torch.max(Outputs.data, 1)
            TotalTrain += Labels.size(0)
            CorrectTrain += (Predicted == torch.argmax(Labels, dim=1)).sum().item()
    TrainingDatasetAccuracy = str(round(100 * (CorrectTrain / TotalTrain), 2)) + "%"

    torch.cuda.empty_cache()

    TotalVal = 0
    CorrectVal = 0
    with torch.no_grad():
        for Data in ValDataLoader:
            Objects, Labels = Data
            Objects, Labels = Objects.to(DEVICE), Labels.to(DEVICE)
            Outputs = BestModel(Objects)
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
                f"object_count#{OBJECT_COUNT}",
                f"resolution#{RESOLUTION}",
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
            if os.path.exists(MODEL_PATH) == False:
                os.makedirs(MODEL_PATH)
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