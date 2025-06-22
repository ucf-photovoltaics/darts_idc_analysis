# Contains functions that produce cleaned and joined versions of the data. Feel
# free to add any functions to this file, and use any functions from here.

import pandas as pd
import numpy as np
import os
import typing

# Change the current working directory to the darts_idc_analysis folder
os.chdir("..")

# read data
master=pd.read_csv("IDCSubmersionMasterlist_20250505.csv")

#-----------------------------------------------------------------------------------
# drop rows with NaN
master=master.dropna(subset=["Solution"])
master=master.dropna(subset=["Voltage"])

# drop columns and rows that are not being used
master=master.drop(master[master["Status"].str.contains("In progress",na=False)].index)
master=master.drop(master[master["Status"].str.contains("Not started",na=False)].index)

# drop columns that are unnecessary
# CV_Post and CF_Post are all NaNs
master=master.drop(["Location", "Date","Notes","CV_Post","CF_Post","Tags"], axis=1)

# Create multilevel column to uniquely identify each sensor
master["Sensor ID"] = master["Board ID"] + "_" + master["Sensor"]

# Fix column naming inconsistency: "CV_Baseline " -> "CV_Baseline"
master["CV_Baseline"] = master["CV_Baseline "]
master.drop(columns="CV_Baseline ", inplace=True)

#-----------------------------------------------------------------------------------
# convert columns to the correct data type
master["Voltage"]=master["Voltage"].astype(int)
# add more here if needed

# Get the cleaned master data
def get_master():
    return master

# Get a DataFrame that is the merging of the master data and all the
# CurrentTime files. Each row represents one current measurement at a given
# time, and it has data about the sensor, solution, etc.
def get_master_current_time():
    current_time_all = [] # List of all currentTime data frames

    # For each row, read the currentTime file if possible, and append it to list
    for _, row in master.iterrows():
        current_in = row["Current"]

        # If current_in is a number, skip
        try:
            float(current_in)
            continue
        except ValueError:
            pass

        # Else, current_in is a file, so read it
        try:
            current_time = pd.read_csv(f"CurrentTime/{current_in}")
        except FileNotFoundError:
            continue
        
        # Add file_name column for joining purposes
        current_time["file_name"] = current_in

        # Append this current_time to current_time_all
        current_time_all.append(current_time)

    # Convert current_time_all, (a list), to a concatenation of all its contents
    current_time_all = pd.concat(current_time_all)

    # Join master with current_time_all
    master_current_time = master.merge(
        current_time_all,
        left_on="Current", right_on="file_name",
        how="inner"
    )

    # The file names are no longer needed
    master_current_time.drop(columns=["file_name", "Current"], inplace=True)

    # Create multilevel column to identify each sensor
    master_current_time["Sensor ID"] = master_current_time["Board ID"] + "_" + master_current_time["Sensor"]

    return master_current_time

# Returns the master merged with the CF_PRISTINE or CV_PRISTINE files, depending
# on given parameter. Merging master with EXPOSED isn't possible due to
# corresponding columns being empty in master
def get_master_pristine(cf_or_cv: typing.Literal["CF", "CV"]):
    pristine_all = [] # List of all pristine DataFrames, either cf or cv

    # For each row, read file, and append to list
    for _, row in master.iterrows():
        # Get file name
        if cf_or_cv == "CF":
            file_name = row["CF_Baseline"]
        else:
            file_name = row["CV_Baseline"]
        
        # Skip if file name is nan
        if file_name == np.nan:
            continue

        # Try reading file, skip if not found
        try:
            pristine = pd.read_csv(f"{cf_or_cv}/{cf_or_cv}_PRISTINE/{file_name}")
        except FileNotFoundError:
            continue
        
        # Add file_name column for joining purposes
        pristine["file_name"] = file_name

        # Append this DataFrame to list
        pristine_all.append(pristine)

    # Convert lists to a concatenation of all their contents
    pristine_all = pd.concat(pristine_all, ignore_index=True)

    # Join master with cf_pristine_all
    master_pristine = master.merge(
        pristine_all,
        left_on=f"{cf_or_cv}_Baseline",
        right_on="file_name",
        how="inner"
    )

    # The file names are no longer needed
    master_pristine.drop(columns=["file_name", f"{cf_or_cv}_Baseline"], inplace=True)

    return master_pristine

# Returns all of the CV or CF files joined together. This will include exposed
# files, which are not available in master_cf_pristine or master_cv_pristine
def get_cf_or_cv_joined(cf_or_cv: typing.Literal["CF", "CV"]):
    # Lists to store DataFrames of pristine and exposed
    pristine_all = []
    exposed_all = []

    # Loop over pristine, and exposed
    for age in ["PRISTINE", "EXPOSED"]:
        # Get folder which has the csv files, such as "CF/CF_EXPOSED"
        folder = f"{cf_or_cv}/{cf_or_cv}_{age}"

        # For each file_name in folder
        for file_name in os.listdir(folder):
            # Read df
            df = pd.read_csv(f"{folder}/{file_name}")

            # Append to list of pristine or exposed
            if age == "PRISTINE":
                pristine_all.append(df)
            else:
                exposed_all.append(df)
    
    # Convert both lists of DataFrames to concatenated DataFrames
    pristine_all = pd.concat(pristine_all, ignore_index=True)
    exposed_all = pd.concat(exposed_all, ignore_index=True)

    # Add column for age, which stores "PRISTINE"|"EXPOSED"
    pristine_all["Age"] = "PRISTINE"
    exposed_all["Age"] = "EXPOSED"

    # Merge pristine and exposed, since they are differentiated by "Age"
    cf_or_cv_joined = pd.concat([pristine_all, exposed_all], ignore_index=True)

    return cf_or_cv_joined
