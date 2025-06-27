# This is the first layer of the pipeline. Each function here will read and
# return a certain type of file in the data. This file standardizes reading each
# file, because there should be only one valid way to read data. Cleaning has
# various possibilities though, so the cleans.py is a separate layer of the
# pipeline. Reading should not lose useful data, while cleaning may.

import pandas as pd
import numpy as np
import cv2
import os
import typing

# Get the master data as a DataFrame with proper data types
# Future idea: Replace all occurrences of file names in cells with their
# DataFrame equivalent
def get_master():
    master = pd.read_csv("IDCSubmersionMasterlist_20250505.csv")

    # Set index to a unique sensor identifier
    master.set_index(["Board ID", "Sensor"], inplace=True, drop=False)
    master.sort_index(inplace=True)

    return master

# Get a CurrentTime file as a DataFrame with proper data types
def get_current_time(file_name: str):
    return

# Get a CF/CV file, (PRISTINE/EXPOSED), as a DataFrame with proper data types
def get_cf_or_cv(file_name: str):
    return

# Stores the coords as percentages of the sensor bounds
# Sample use: pattern_to_sensor_to_coords[pattern][sensor]["x1"|"y2"...]
pattern_to_sensor_to_coords = {
    1: {
        "U1": {"x1":0.1012, "x2":0.3067, "y1":0.576, "y2":0.6601},
        "U2": {"x1":0.1377, "x2":0.2395, "y1":0.09905, "y2":0.2684},
        "U3": {"x1":0.7647, "x2":0.8325, "y1":0.07259, "y2":0.3275},
        "U4": {"x1":0.7736, "x2":0.8254, "y1":0.434, "y2":0.7743}
    },
    4: {
        "U1": {"x1":0.09917, "x2":0.3052, "y1":0.5761, "y2":0.6606},
        "U2": {"x1":0.1369, "x2":0.2389, "y1":0.09948, "y2":0.2688},
        "U3": {"x1":0.7653, "x2":0.8328, "y1":0.07529, "y2":0.3299},
        "U4": {"x1":0.773, "x2":0.8243, "y1":0.4364, "y2":0.7764}
    },
    7: {
        "U1": {"x1":0.1011, "x2":0.3066, "y1":0.5776, "y2":0.6608},
        "U2": {"x1":0.137, "x2":0.2387, "y1":0.1002, "y2":0.2691},
        "U3": {"x1":0.7646, "x2":0.8324, "y1":0.07282, "y2":0.3275},
        "U4": {"x1":0.7737, "x2":0.8255, "y1":0.4342, "y2":0.7739}
    },
    10: {
        "U1": {"x1":0.09913, "x2":0.3055, "y1":0.5753, "y2":0.6594},
        "U2": {"x1":0.1367, "x2":0.2384, "y1":0.0993, "y2":0.2683},
        "U3": {"x1":0.7644, "x2":0.8324, "y1":0.07448, "y2":0.3286},
        "U4": {"x1":0.7727, "x2":0.8243, "y1":0.4351, "y2":0.7745}
    }
}

# Get a cropped image of a sensor, given (Board ID, Sensor), and EXPOSED or
# PRISTINE
def get_sensor_image(master_index: tuple, age: typing.Literal["EXPOSED", "PRISTINE"]):
    board_id, sensor = master_index

    # Get list of file names that start with this board ID
    matching_file_names = [file for file in os.listdir(f"Imgscans_{age}_edited") if file.startswith(board_id)]
    # If no files are found, return nan
    if len(matching_file_names) == 0:
        return np.nan
    
    # Take the first found file and use it
    file_name = matching_file_names[0]

    # Read board image
    board_img = cv2.imread(f"Imgscans_{age}_edited/{file_name}")

    # Get width and height, to be used for calculating crop coords
    height, width, _ = board_img.shape
    # Get pattern
    pattern = int(board_id.split("_")[1])
    # Calculate crop coords based on crop percentages
    coords = pattern_to_sensor_to_coords[pattern][sensor]
    x1 = round(coords["x1"] * width)
    x2 = round(coords["x2"] * width)
    y1 = round(coords["y1"] * height)
    y2 = round(coords["y2"] * height)

    # Return the cropped version
    return board_img[y1:y2, x1:x2]
