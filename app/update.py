import requests
import zipfile
import shutil
import os

AppPath = str(os.path.dirname(os.path.dirname(__file__))).replace("\\", "/")
AppPath += "/" if AppPath[-1] != "/" else ""

RepositoryURL = "https://github.com/OleFranz/PyTorch-Calculator/archive/refs/heads/main.zip"
DestinationPath = f"{AppPath}cache/PyTorch-Calculator-Update.zip"

os.makedirs(os.path.dirname(DestinationPath), exist_ok=True)

Response = requests.get(RepositoryURL, allow_redirects=True, stream=True)
with open(DestinationPath, "wb") as File:
    File.write(Response.content)

FoldersToIgnore = [
    f"{AppPath}.vscode",
    f"{AppPath}.vs",
    f"{AppPath}.git",
    f"{AppPath}python",
    f"{AppPath}cache",
    f"{AppPath}cpp-app/.vscode",
    f"{AppPath}cpp-app/.vs",
    f"{AppPath}cpp-app/.git",
    f"{AppPath}cpp-app/build",
    f"{AppPath}train/dataset/final",
    f"{AppPath}train/dataset/raw",
    f"{AppPath}train/models",
    f"{AppPath}train/tensorboard"
]

FilesToIgnore = [
    f"{AppPath}config/settings.json"
]

FilesToInclude = [
    f"{AppPath}train/dataset/final/README.md",
    f"{AppPath}train/dataset/raw/README.md",
    f"{AppPath}train/models/README.md"
]

FilesToDelete = []

for FolderPath, _, Files in os.walk(AppPath, topdown=False):
    FolderPath = str(FolderPath).replace("\\", "/")
    FolderPath += "/" if FolderPath[-1] != "/" else ""
    for File in Files:
        FilePath = f"{FolderPath}{File}"

        Ignore = False
        for Folder in FoldersToIgnore:
            if f"{FilePath}/".startswith(f"{Folder}/"):
                Ignore = True
                break
        if not Ignore:
            FilesToDelete.append(FilePath)

for File in FilesToIgnore:
    if File in FilesToDelete:
        FilesToDelete.remove(File)

for File in FilesToInclude:
    if File not in FilesToDelete:
        FilesToDelete.append(File)

for File in FilesToDelete:
    try: os.remove(File)
    except: pass

for FolderPath, _, Files in os.walk(AppPath, topdown=False):
    if Files == []:
        try: os.rmdir(FolderPath)
        except: pass

with zipfile.ZipFile(DestinationPath, 'r') as ZipFile:
    ZipFile.extractall(DestinationPath.replace(".zip", ""))

try: os.remove(DestinationPath)
except: pass

CopySourceFolder = DestinationPath.replace(".zip", "")
for FolderPath, _, Files in os.walk(DestinationPath.replace(".zip", "")):
    if Files != []:
        CopySourceFolder = FolderPath.replace("\\", "/")
        break

CopyDestinationFolder = AppPath

try:
    shutil.copytree(CopySourceFolder, CopyDestinationFolder, dirs_exist_ok=True)
except:
    pass

try: shutil.rmtree(DestinationPath.replace(".zip", ""))
except: pass