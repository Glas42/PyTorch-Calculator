import datetime
print(f"\n----------------------------------------------\n\n\033[90m[{datetime.datetime.now().strftime('%H:%M:%S')}] \033[0mImporting libraries...")

import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

from torch.utils.tensorboard import SummaryWriter
from torch.utils.data import Dataset, DataLoader
from torch.cuda.amp import GradScaler, autocast
import torch.optim.lr_scheduler as lr_scheduler
from torchvision import transforms, utils
import multiprocessing
import torch.nn as nn
from PIL import Image
import numpy as np
import threading
import shutil
import torch
import time
import cv2

# Constants
PATH = os.path.dirname(__file__)
DATA_PATH = os.path.join(PATH, "dataset")
MODEL_PATH = os.path.join(PATH, "model")
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
NUM_EPOCHS = 10000
BATCH_SIZE = 10
LATENT_DIM = 10
BETA1 = 0.9
BETA2 = 0.9
IMG_WIDTH = 64
IMG_HEIGHT = 64
LEARNING_RATE = 0.001
NUM_WORKERS = 0
SHUFFLE = True
PIN_MEMORY = False

CLASSES = {
    "0": 0,
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "x": 10,
    "y": 11,
    "z": 12,
}
NUM_CLASSES = len(CLASSES)

IMG_COUNT = 0
for file in os.listdir(DATA_PATH):
    if file.endswith(".png"):
        IMG_COUNT += 1
if IMG_COUNT == 0:
    print("No images found, exiting...")
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
print(timestamp() + "> Classes:", NUM_CLASSES)
print(timestamp() + "> Latent dim:", LATENT_DIM)
print(timestamp() + "> Beta 1:", BETA1)
print(timestamp() + "> Beta 2:", BETA2)
print(timestamp() + "> Images:", IMG_COUNT)
print(timestamp() + "> Image width:", IMG_WIDTH)
print(timestamp() + "> Image height:", IMG_HEIGHT)
print(timestamp() + "> Learning rate:", LEARNING_RATE)
print(timestamp() + "> Number of workers:", NUM_WORKERS)
print(timestamp() + "> Shuffle:", SHUFFLE)
print(timestamp() + "> Pin memory:", PIN_MEMORY)


def load_data():
    images = []
    user_inputs = []
    print(f"\r{timestamp()}Loading dataset...", end='', flush=True)
    for file in os.listdir(DATA_PATH):
        if file.endswith(".png"):
            img = Image.open(os.path.join(DATA_PATH, file)).convert('L')  # Convert to grayscale
            img = np.array(img)
            img = cv2.resize(img, (IMG_WIDTH, IMG_HEIGHT))
            img = img / 255.0  # Normalize the image

            user_inputs_file = os.path.join(DATA_PATH, file.replace(".png", ".txt"))
            if os.path.exists(user_inputs_file):
                with open(user_inputs_file, 'r') as f:
                    content = str(f.read())
                    if content.isdigit() and 0 <= int(content) < NUM_CLASSES:
                        user_input = [0] * NUM_CLASSES
                        user_input[int(content)] = 1
                images.append(img)
                user_inputs.append(user_input)
            else:
                pass

        if len(images) % 100 == 0:
            print(f"\r{timestamp()}Loading dataset... ({round(100 * len(images) / IMG_COUNT)}%)", end='', flush=True)

    return np.array(images, dtype=np.float32), np.array(user_inputs, dtype=np.float32)


# Custom dataset class
class CustomDataset(Dataset):
    def __init__(self, images, user_inputs, transform=None):
        self.images = images
        self.user_inputs = user_inputs
        self.transform = transform

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        image = self.images[idx]
        user_input = self.user_inputs[idx]
        image = self.transform(image)
        return image, torch.as_tensor(user_input, dtype=torch.float32)


# Define the generator
class Generator(nn.Module):
    def __init__(self):
        super(Generator, self).__init__()
        self.main = nn.Sequential(
            nn.ConvTranspose2d(LATENT_DIM + NUM_CLASSES, 512, 4, 1, 0, bias=False),
            nn.BatchNorm2d(512),
            nn.ReLU(True),
            nn.ConvTranspose2d(512, 256, 4, 2, 1, bias=False),
            nn.BatchNorm2d(256),
            nn.ReLU(True),
            nn.ConvTranspose2d(256, 128, 4, 2, 1, bias=False),
            nn.BatchNorm2d(128),
            nn.ReLU(True),
            nn.ConvTranspose2d(128, 64, 4, 2, 1, bias=False),
            nn.BatchNorm2d(64),
            nn.ReLU(True),
            nn.ConvTranspose2d(64, 1, 4, 2, 1, bias=False),
            nn.Tanh()
        )

    def forward(self, input):
        return self.main(input)


# Define the discriminator
class Discriminator(nn.Module):
    def __init__(self):
        super(Discriminator, self).__init__()
        self.main = nn.Sequential(
            nn.Conv2d(1, 32, 4, 2, 1, bias=False),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Conv2d(32, 64, 4, 2, 1, bias=False),
            nn.BatchNorm2d(64),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Conv2d(64, 128, 4, 2, 1, bias=False),
            nn.BatchNorm2d(128),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Conv2d(128, 256, 4, 2, 1, bias=False),
            nn.BatchNorm2d(256),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Conv2d(256, NUM_CLASSES, 4, 1, 0, bias=False),
            nn.Sigmoid()
        )

    def forward(self, input):
        return self.main(input).view(input.size(0), -1)


def main():    
    # Initialize generator and discriminator
    generator = Generator().to(DEVICE)
    discriminator = Discriminator().to(DEVICE)

    def get_model_size_mb(model):
        total_params = 0
        for param in model.parameters():
            total_params += np.prod(param.size())
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        non_trainable_params = total_params - trainable_params
        bytes_per_param = next(model.parameters()).element_size()
        model_size_mb = (total_params * bytes_per_param) / (1024 ** 2)
        return total_params, trainable_params, non_trainable_params, model_size_mb

    total_g_params, trainable_g_params, non_trainable_g_params, g_model_size_mb = get_model_size_mb(generator)
    total_d_params, trainable_d_params, non_trainable_d_params, d_model_size_mb = get_model_size_mb(discriminator)

    print()
    print(timestamp() + "Model properties:")
    print(timestamp() + f"> Generator total parameters: {total_g_params}")
    print(timestamp() + f"> Generator trainable parameters: {trainable_g_params}")
    print(timestamp() + f"> Generator non-trainable parameters: {non_trainable_g_params}")
    print(timestamp() + f"> Generator predicted model size: {g_model_size_mb:.2f}MB")
    print(timestamp() + f"> Discriminator total parameters: {total_d_params}")
    print(timestamp() + f"> Discriminator trainable parameters: {trainable_d_params}")
    print(timestamp() + f"> Discriminator non-trainable parameters: {non_trainable_d_params}")
    print(timestamp() + f"> Discriminator predicted model size: {d_model_size_mb:.2f}MB")

    print("\n----------------------------------------------\n")

    print(timestamp() + "Loading...")

    # Load data
    images, user_inputs = load_data()

    # Load data
    transform = transforms.Compose([
        transforms.ToTensor(),
    ])

    # Create dataset
    dataset = CustomDataset(images, user_inputs, transform=transform)
    dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=SHUFFLE, num_workers=NUM_WORKERS, pin_memory=PIN_MEMORY)

    # Loss function and optimizers
    scaler = GradScaler()
    criterion = nn.BCEWithLogitsLoss()
    generator_optimizer = torch.optim.Adam(generator.parameters(), lr=LEARNING_RATE, betas=(BETA1, BETA2))
    generator_scheduler = lr_scheduler.OneCycleLR(generator_optimizer, max_lr=LEARNING_RATE, steps_per_epoch=len(dataloader), epochs=NUM_EPOCHS)
    discriminator_optimizer = torch.optim.Adam(discriminator.parameters(), lr=LEARNING_RATE, betas=(BETA1, BETA2))
    discriminator_scheduler = lr_scheduler.OneCycleLR(discriminator_optimizer, max_lr=LEARNING_RATE, steps_per_epoch=len(dataloader), epochs=NUM_EPOCHS)

    # Create tensorboard logs folder if it doesn't exist
    if not os.path.exists(f"{PATH}/logs"):
        os.makedirs(f"{PATH}/logs")

    # Delete previous tensorboard logs
    for obj in os.listdir(f"{PATH}/logs"):
        try:
            shutil.rmtree(f"{PATH}/logs/{obj}")
        except:
            os.remove(f"{PATH}/logs/{obj}")

    # Tensorboard setup
    summary_writer = SummaryWriter(f"{PATH}/logs", comment="Generative-Adversarial-Network-Training", flush_secs=20)

    print(f"\r{timestamp()}Starting training...                       ")
    print("\n-----------------------------------------------------------------------------------------------------------\n")

    training_time_prediction = time.time()
    training_start_time = time.time()
    epoch_total_time = 0
    generator_loss = 0
    discriminator_loss = 0
    training_epoch = 0

    global PROGRESS_PRINT
    PROGRESS_PRINT = "initializing"
    def training_progress_print():
        global PROGRESS_PRINT
        def num_to_str(num: int):
            str_num = format(num, '.15f')
            while len(str_num) > 15:
                str_num = str_num[:-1]
            while len(str_num) < 15:
                str_num = str_num + '0'
            return str_num
        while PROGRESS_PRINT == "initializing":
            time.sleep(1)
        while PROGRESS_PRINT == "running":

            progress = (time.time() - epoch_total_start_time) / epoch_total_time
            if progress > 1: progress = 1
            if progress < 0: progress = 0

            progress = '█' * int(progress * 10) + '░' * (10 - int(progress * 10))
            epoch_time = round(epoch_total_time, 2) if epoch_total_time > 1 else round((epoch_total_time) * 1000)
            eta = time.strftime('%H:%M:%S', time.gmtime(round((training_time_prediction - training_start_time) / (training_epoch + 1) * NUM_EPOCHS - (training_time_prediction - training_start_time) + (training_time_prediction - time.time()), 2)))

            print(f"\r{progress} Epoch {training_epoch+1}, Generator Loss: {num_to_str(generator_loss)}, Discriminator Loss: {num_to_str(discriminator_loss)}, {epoch_time}{'s' if epoch_total_time > 1 else 'ms'}/Epoch, ETA: {eta}                       ", end='', flush=True)

            time.sleep(epoch_total_time/10 if epoch_total_time/10 >= 0.1 else 0.1)
        if PROGRESS_PRINT == "early stopped":
            print(f"\rEarly stopping at Epoch {training_epoch+1}, Generator Loss: {num_to_str(generator_loss)}, Discriminator Loss: {num_to_str(discriminator_loss)}                                              ", end='', flush=True)
        elif PROGRESS_PRINT == "finished":
            print(f"\rFinished at Epoch {training_epoch+1}, Generator Loss: {num_to_str(generator_loss)}, Discriminator Loss: {num_to_str(discriminator_loss)}                                              ", end='', flush=True)
        PROGRESS_PRINT = "received"
    threading.Thread(target=training_progress_print, daemon=True).start()

    for epoch in range(NUM_EPOCHS):
        epoch_total_start_time = time.time()

        generator.train()
        running_generator_loss = 0.0
        for i, data in enumerate(dataloader, 0):
            inputs, labels = data[0].to(DEVICE, non_blocking=True), data[1].to(DEVICE, non_blocking=True)
            generator_optimizer.zero_grad()
            with autocast():
                latent_input = torch.randn(inputs.size(0), LATENT_DIM, 1, 1, device=DEVICE)
                labels = labels.unsqueeze(2).unsqueeze(3)
                combined_input = torch.cat((latent_input, labels), dim=1)
                outputs = generator(combined_input)
                loss = criterion(outputs, inputs)
            scaler.scale(loss).backward()
            scaler.step(generator_optimizer)
            scaler.update()
            generator_scheduler.step()
            running_generator_loss += loss.item()
        running_generator_loss /= len(dataloader)
        generator_loss = running_generator_loss

        discriminator.train()
        running_discriminator_loss = 0.0
        for i, data in enumerate(dataloader, 0):
            inputs, labels = data[0].to(DEVICE, non_blocking=True), data[1].to(DEVICE, non_blocking=True)
            discriminator_optimizer.zero_grad()
            with autocast():
                outputs = discriminator(inputs)
                loss = criterion(outputs, labels)
            scaler.scale(loss).backward()
            scaler.step(discriminator_optimizer)
            scaler.update()
            discriminator_scheduler.step()
            running_discriminator_loss += loss.item()
        running_discriminator_loss /= len(dataloader)
        discriminator_loss = running_discriminator_loss

        epoch_total_time = time.time() - epoch_total_start_time

        if epoch % 100 == 0:
            num_classes = NUM_CLASSES
            num_rows = int(np.ceil(np.sqrt(num_classes)))
            num_cols = num_rows
            grid_size = num_rows * num_cols
            all_images = torch.zeros(grid_size, 1, IMG_HEIGHT, IMG_WIDTH)
            for i in range(grid_size):
                if i < num_classes:
                    class_label = torch.zeros(1, NUM_CLASSES, 1, 1, device=DEVICE)
                    class_label[0, i % NUM_CLASSES, 0, 0] = 1
                    input = torch.cat((torch.randn(1, LATENT_DIM, 1, 1, device=DEVICE), class_label), dim=1)
                    image = generator(input)
                    all_images[i] = image[0].detach().cpu()
                else:
                    all_images[i] = torch.zeros(1, 1, IMG_HEIGHT, IMG_WIDTH)

            grid_image = utils.make_grid(all_images, nrow=num_cols)
            grid_image = (grid_image + 1) / 2
            grid_image = (grid_image * 255).type(torch.uint8).permute(1, 2, 0).numpy()
            summary_writer.add_image(f'Generated Images', grid_image, epoch + 1, dataformats='HWC')

        # Log values to Tensorboard
        summary_writer.add_scalars(f'Stats', {
            'generator_loss': generator_loss,
            'discriminator_loss': discriminator_loss,
            'epoch_time': epoch_total_time
        }, epoch + 1)
        training_epoch = epoch
        training_time_prediction = time.time()
        PROGRESS_PRINT = "running"

    if PROGRESS_PRINT != "early stopped":
        PROGRESS_PRINT = "finished"
    while PROGRESS_PRINT != "received":
        time.sleep(1)

    print("\n\n-----------------------------------------------------------------------------------------------------------")

    TRAINING_TIME = time.strftime('%H-%M-%S', time.gmtime(time.time() - training_start_time))
    TRAINING_DATE = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

    print()
    print(timestamp() + f"Training completed after " + TRAINING_TIME.replace('-', ':'))

    # Save the generator model
    print(timestamp() + "Saving the generator model...")

    metadata_optimizer = str(generator_optimizer).replace('\n', '')
    metadata_criterion = str(criterion).replace('\n', '')
    metadata_model = str(generator).replace('\n', '')
    metadata = (f"epochs#{epoch+1}",
                f"batch#{BATCH_SIZE}",
                f"classes#{CLASSES}",
                f"outputs#{CLASSES}",
                f"image_count#{IMG_COUNT}",
                f"image_width#{IMG_WIDTH}",
                f"image_height#{IMG_HEIGHT}",
                f"learning_rate#{LEARNING_RATE}",
                f"number_of_workers#{NUM_WORKERS}",
                f"shuffle#{SHUFFLE}",
                f"pin_memory#{PIN_MEMORY}",
                f"training_time#{TRAINING_TIME}",
                f"training_date#{TRAINING_DATE}",
                f"training_device#{DEVICE}",
                f"training_os#{os.name}",
                f"architecture#{metadata_model}",
                f"torch_version#{torch.__version__}",
                f"numpy_version#{np.__version__}",
                f"pil_version#{Image.__version__}",
                f"transform#{transform}",
                f"optimizer#{metadata_optimizer}",
                f"loss_function#{metadata_criterion}",
                f"dataset_size#{len(dataset)}",
                f"loss#{generator_loss}")
    metadata = {"data": metadata}
    metadata = {data: str(value).encode("ascii") for data, value in metadata.items()}

    generator_saved = False
    for i in range(5):
        try:
            gen_model = torch.jit.script(generator)
            torch.jit.save(gen_model, os.path.join(MODEL_PATH, f"Generator-{TRAINING_DATE}.pt"), _extra_files=metadata)
            generator_saved = True
            break
        except:
            print(timestamp() + "Failed to save the generator model. Retrying...")
    print(timestamp() + "Generator model saved successfully.") if generator_saved else print(timestamp() + "Failed to save the generator model.")

    # Save the discriminator model
    print(timestamp() + "Saving the discriminator model...")

    metadata_optimizer = str(discriminator_optimizer).replace('\n', '')
    metadata_criterion = str(criterion).replace('\n', '')
    metadata_model = str(discriminator).replace('\n', '')
    metadata = (f"epochs#{epoch+1}",
                f"batch#{BATCH_SIZE}",
                f"classes#{CLASSES}",
                f"outputs#{CLASSES}",
                f"image_count#{IMG_COUNT}",
                f"image_width#{IMG_WIDTH}",
                f"image_height#{IMG_HEIGHT}",
                f"learning_rate#{LEARNING_RATE}",
                f"number_of_workers#{NUM_WORKERS}",
                f"shuffle#{SHUFFLE}",
                f"pin_memory#{PIN_MEMORY}",
                f"training_time#{TRAINING_TIME}",
                f"training_date#{TRAINING_DATE}",
                f"training_device#{DEVICE}",
                f"training_os#{os.name}",
                f"architecture#{metadata_model}",
                f"torch_version#{torch.__version__}",
                f"numpy_version#{np.__version__}",
                f"pil_version#{Image.__version__}",
                f"transform#{transform}",
                f"optimizer#{metadata_optimizer}",
                f"loss_function#{metadata_criterion}",
                f"dataset_size#{len(dataset)}",
                f"loss#{discriminator_loss}")
    metadata = {"data": metadata}
    metadata = {data: str(value).encode("ascii") for data, value in metadata.items()}

    discriminator_saved = False
    for i in range(5):
        try:
            dis_model = torch.jit.script(discriminator)
            torch.jit.save(dis_model, os.path.join(MODEL_PATH, f"Discriminator-{TRAINING_DATE}.pt"), _extra_files=metadata)
            discriminator_saved = True
            break
        except:
            print(timestamp() + "Failed to save the discriminator model. Retrying...")
    print(timestamp() + "Discriminator model saved successfully.") if discriminator_saved else print(timestamp() + "Failed to save the discriminator model.")

    print("\n----------------------------------------------\n")

if __name__ == '__main__':
    main()