import datetime
import os
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import torchvision.utils as vutils
from torchvision import transforms
import numpy as np
from PIL import Image
import shutil
import time
import threading

# Constants
PATH = os.path.dirname(__file__)
DATA_PATH = os.path.join(PATH, "dataset")
MODEL_PATH = os.path.join(PATH, "model")
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
NUM_EPOCHS = 10000
BATCH_SIZE = 3
LATENT_DIM = 10
IMG_WIDTH = 64
IMG_HEIGHT = 64
IMG_CHANNELS = 1
LEARNING_RATE = 0.001
BETA1 = 0.001
BETA2 = 0.999
NUM_WORKERS = 0
SHUFFLE = True
PIN_MEMORY = False

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

# Custom dataset class
class CustomDataset(Dataset):
    def __init__(self, images, transform=None):
        self.images = images
        self.transform = transform

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        image = self.images[idx]
        # Convert the image to grayscale
        image = image.convert('L')
        if self.transform:
            image = self.transform(image)
        return image

# Define the generator
class Generator(nn.Module):
    def __init__(self):
        super(Generator, self).__init__()
        self.main = nn.Sequential(
            nn.ConvTranspose2d(LATENT_DIM, 512, 4, 1, 0, bias=False),
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
            nn.ConvTranspose2d(64, IMG_CHANNELS, 4, 2, 1, bias=False),
            nn.Tanh()
        )

    def forward(self, input):
        return self.main(input)

# Define the discriminator
class Discriminator(nn.Module):
    def __init__(self):
        super(Discriminator, self).__init__()
        self.main = nn.Sequential(
            nn.Conv2d(IMG_CHANNELS, 32, 4, 2, 1, bias=False),
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
            nn.Conv2d(256, 1, 4, 1, 0, bias=False),
            nn.Sigmoid()
        )

    def forward(self, input):
        return self.main(input)

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
    transform = transforms.Compose([
        transforms.Resize((IMG_HEIGHT, IMG_WIDTH)),
        transforms.ToTensor(),
        transforms.Normalize((0.5,), (0.5,))
    ])
    dataset = CustomDataset([Image.open(os.path.join(DATA_PATH, file)).convert('RGB') for file in os.listdir(DATA_PATH) if file.endswith(".png")], transform=transform)
    dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=SHUFFLE, num_workers=NUM_WORKERS, pin_memory=PIN_MEMORY)

    # Loss function and optimizers
    criterion = nn.BCELoss()
    g_optimizer = torch.optim.Adam(generator.parameters(), lr=LEARNING_RATE, betas=(BETA1, BETA2))
    d_optimizer = torch.optim.Adam(discriminator.parameters(), lr=LEARNING_RATE, betas=(BETA1, BETA2))

    # Create tensorboard logs folder if it doesn't exist
    if not os.path.exists(f"{PATH}/AI/Generation/logs"):
        os.makedirs(f"{PATH}/AI/Generation/logs")

    # Delete previous tensorboard logs
    for obj in os.listdir(f"{PATH}/AI/Generation/logs"):
        try:
            shutil.rmtree(f"{PATH}/AI/Generation/logs/{obj}")
        except:
            os.remove(f"{PATH}/AI/Generation/logs/{obj}")

    print(f"\r{timestamp()}Starting training...                       ")
    print("\n-----------------------------------------------------------------------------------------------------------\n")

    training_time_prediction = time.time()
    training_start_time = time.time()
    epoch_total_time = 0
    g_loss = 0
    d_loss = 0
    training_epoch = 0

    global PROGRESS_PRINT
    PROGRESS_PRINT = "initializing"
    def training_progress_print():
        global PROGRESS_PRINT
        def num_to_str(num: float):
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

            print(f"\r{progress} Epoch {training_epoch+1}, G Loss: {num_to_str(g_loss)}, D Loss: {num_to_str(d_loss)}, {epoch_time}{'s' if epoch_total_time > 1 else 'ms'}/Epoch, ETA: {eta}                       ", end='', flush=True)

            time.sleep(epoch_total_time/10 if epoch_total_time/10 >= 0.1 else 0.1)
        if PROGRESS_PRINT == "early stopped":
            print(f"\rEarly stopping at Epoch {training_epoch+1}, G Loss: {num_to_str(g_loss)}, D Loss: {num_to_str(d_loss)}                                              ", end='', flush=True)
        elif PROGRESS_PRINT == "finished":
            print(f"\rFinished at Epoch {training_epoch+1}, G Loss: {num_to_str(g_loss)}, D Loss: {num_to_str(d_loss)}                                              ", end='', flush=True)
        PROGRESS_PRINT = "received"
    threading.Thread(target=training_progress_print, daemon=True).start()

    # Increase the number of discriminator updates per generator update
    d_steps = 1
    g_steps = 1


    for epoch in range(NUM_EPOCHS):
        epoch_total_start_time = time.time()

        for _ in range(d_steps):
            discriminator.zero_grad()
            real_images = next(iter(dataloader)).to(DEVICE)
            real_output = discriminator(real_images)
            real_loss = criterion(real_output, torch.ones_like(real_output))

            noise = torch.randn(BATCH_SIZE, LATENT_DIM, 1, 1, device=DEVICE)
            fake_images = generator(noise)
            fake_output = discriminator(fake_images.detach())
            fake_loss = criterion(fake_output, torch.zeros_like(fake_output))
            d_loss = (real_loss + fake_loss) / 2
            d_loss.backward()
            d_optimizer.step()

        # Train the generator
        for _ in range(g_steps):
            generator.zero_grad()
            fake_output = discriminator(fake_images)
            g_loss = criterion(fake_output, torch.ones_like(fake_output))
            g_loss.backward()
            g_optimizer.step()

        epoch_total_time = time.time() - epoch_total_start_time

        training_epoch = epoch
        training_time_prediction = time.time()
        PROGRESS_PRINT = "running"
        
        if (epoch + 1) % 100 == 0:
            # Generate examples
            fixed_noise = torch.randn(64, LATENT_DIM, 1, 1, device=DEVICE)
            with torch.no_grad():
                fake_images = generator(fixed_noise)
            
            # Save the generated images
            img_grid = vutils.make_grid(fake_images.detach().cpu(), padding=2, normalize=True)
            
            # Save the images to disk
            if not os.path.exists(MODEL_PATH):
                os.makedirs(MODEL_PATH)
            vutils.save_image(fake_images.detach().cpu(),
                            os.path.join(MODEL_PATH, f"generated_images_epoch_{epoch + 1}.png"),
                            padding=2, normalize=True)

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

    metadata_g_optimizer = str(g_optimizer).replace('\n', '')
    metadata_g_criterion = str(criterion).replace('\n', '')
    metadata_generator = str(generator).replace('\n', '')
    metadata = (f"epochs#{epoch+1}",
                f"batch#{BATCH_SIZE}",
                f"latent_dim#{LATENT_DIM}",
                f"image_width#{IMG_WIDTH}",
                f"image_height#{IMG_HEIGHT}",
                f"image_channels#{IMG_CHANNELS}",
                f"learning_rate#{LEARNING_RATE}",
                f"beta1#{BETA1}",
                f"beta2#{BETA2}",
                f"number_of_workers#{NUM_WORKERS}",
                f"training_time#{TRAINING_TIME}",
                f"training_date#{TRAINING_DATE}",
                f"training_device#{DEVICE}",
                f"training_os#{os.name}",
                f"generator_architecture#{metadata_generator}",
                f"torch_version#{torch.__version__}",
                f"numpy_version#{np.__version__}",
                f"pil_version#{Image.__version__}",
                f"transform#{transform}",
                f"generator_optimizer#{metadata_g_optimizer}",
                f"loss_function#{metadata_g_criterion}")
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
    metadata_d_optimizer = str(d_optimizer).replace('\n', '')
    metadata_d_criterion = str(criterion).replace('\n', '')
    metadata_discriminator = str(discriminator).replace('\n', '')
    metadata = (f"epochs#{epoch+1}",
                f"batch#{BATCH_SIZE}",
                f"latent_dim#{LATENT_DIM}",
                f"image_width#{IMG_WIDTH}",
                f"image_height#{IMG_HEIGHT}",
                f"image_channels#{IMG_CHANNELS}",
                f"learning_rate#{LEARNING_RATE}",
                f"beta1#{BETA1}",
                f"beta2#{BETA2}",
                f"number_of_workers#{NUM_WORKERS}",
                f"training_time#{TRAINING_TIME}",
                f"training_date#{TRAINING_DATE}",
                f"training_device#{DEVICE}",
                f"training_os#{os.name}",
                f"discriminator_architecture#{metadata_discriminator}",
                f"torch_version#{torch.__version__}",
                f"numpy_version#{np.__version__}",
                f"pil_version#{Image.__version__}",
                f"transform#{transform}",
                f"discriminator_optimizer#{metadata_d_optimizer}",
                f"loss_function#{metadata_d_criterion}")
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