# This is the first layer of the pipeline. Each function here will read and
# return a certain type of file in the data. This file standardizes reading each
# file, because there should be only one valid way to read data. Cleaning has
# various possibilities though, so the cleans.py is a separate layer of the
# pipeline. Reading should not lose useful data, while cleaning may.

import pandas as pd
import typing

# Get the master data as a DataFrame with proper data types
# Future idea: Replace all occurrences of file names in cells with their
# DataFrame equivalent
def get_master():
    master = pd.read_csv("IDCSubmersionMasterlist_20250505.csv")

    # Fix datatypes

    return master

# Get a CurrentTime file as a DataFrame with proper data types
def get_current_time(file_name: str):
    return

# Get a CF/CV file, (PRISTINE/EXPOSED), as a DataFrame with proper data types
def get_cf_or_cv(file_name: str):
    return

# Get a cropped image of a sensor, given the board image and sensor
def get_sensor_image(file_name: str, sensor: typing.Literal["U1", "U2", "U3", "U4"]):
    return
