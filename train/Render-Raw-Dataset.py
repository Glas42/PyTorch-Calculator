print("Initializing...")

import numpy as np
import cv2
import os

PATH = os.path.dirname(__file__) + "\\"
DATA_FOLDER = PATH + "dataset\\"
RAW_DATA_FOLDER = PATH + "raw_dataset\\"

resolution = input("Resolution: ")
if not resolution.isnumeric() or int(resolution) <= 1:
    print(f"Invalid resolution {resolution}, defaulting to 512x512")
    resolution = 512
resolution = int(resolution)

thickness = input("Text Thickness: ")
if not thickness.isnumeric() or int(thickness) <= 0:
    print(f"Invalid thickness {thickness}, defaulting to 1")
    thickness = 1
thickness = int(thickness)

if len(os.listdir(DATA_FOLDER)) > 0:
    previous_dataset = input("Previous dataset found, what to do?\nr: remove old data\na: append new data to the old data\n")
    if previous_dataset.lower() == "r":
        for file in os.listdir(DATA_FOLDER):
            os.remove(DATA_FOLDER + file)
    elif previous_dataset.lower() == "a":
        pass
    else:
        print("Invalid input, exiting...")
        exit()

print("\nRendering...")

for file in os.listdir(RAW_DATA_FOLDER):
    frame = np.zeros((resolution, resolution, 1), np.uint8)
    with open(RAW_DATA_FOLDER + file, "r") as f:
        content = str(f.read()).split("#")
        content_class, content_points = content
        list = eval(content_points)
        for points in list:
            last_point = None
            for point in points:
                if last_point == None:
                    last_point = point
                cv2.line(frame, (round(last_point[0] * (resolution - thickness * 2) + thickness), round(last_point[1] * (resolution - thickness * 2) + thickness)), (round(point[0] * (resolution - thickness * 2) + thickness), round(point[1] * (resolution - thickness * 2) + thickness)), (255, 255, 255), thickness)
                last_point = point
        name = str(round(len(os.listdir(DATA_FOLDER)) / 2))
        cv2.imwrite(DATA_FOLDER + name + ".png", frame)
        with open(DATA_FOLDER + name + ".txt", "w", encoding="utf-8") as f:
            f.write(content_class)
            f.close()

print("Done!")