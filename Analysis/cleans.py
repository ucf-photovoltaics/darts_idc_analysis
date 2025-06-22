# Contains functions that produce cleaned and joined versions of the data. Feel
# free to add any functions to this file, and use any functions from here.

import pandas as pd
import numpy as np
import os

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
master=master.drop(["Location", "Date","Notes","CV_Post","CF_Post","Tags"], axis=1)

# Create multilevel column to uniquely identify each sensor
master["Sensor ID"] = master["Board ID"] + "_" + master["Sensor"]

#-----------------------------------------------------------------------------------
# convert columns to the correct data type
master["Voltage"]=master["Voltage"].astype(int)
# add more here if needed

# Get the cleaned master data
def get_master():
    return master

# Get a DataFrame that is the merging of the master data and all the
# CurrentTime files. Each row represents one current measurement at a given
# time, and it has data about the sensor, solution, etc. I used this to easily
# plot current vs time.
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

# Get the result of joining master with CF_pristine
# Pristine is the only valid option because the CF_Post column is empty
def get_master_cf_pristine():
    cf_pristine_all = [] # List of all CF pristine data frames

    # For each row, read CF file, and append to list
    for _, row in master.iterrows():
        # Get cf file name
        cf_file_name = row["CF_Baseline"]
        
        # Skip if file name is nan
        if cf_file_name == np.nan:
            continue

        # Try reading file, skip if not found
        try:
            cf = pd.read_csv(f"CF/CF_PRISTINE/{cf_file_name}")
        except FileNotFoundError:
            continue
        
        # Add file_name column for joining purposes
        cf["file_name"] = cf_file_name

        # Append this DataFrame to list
        cf_pristine_all.append(cf)

    # Convert lists to a concatenation of all their contents
    cf_pristine_all = pd.concat(cf_pristine_all)

    # Join master with cf_pristine_all
    master_cf_pristine = master.merge(
        cf_pristine_all,
        left_on="CF_Baseline", right_on="file_name",
        how="inner"
    )

    # The file names are no longer needed
    master_cf_pristine.drop(columns=["file_name", "Current"], inplace=True)

    return master_cf_pristine

# Get the result of joining master with CV_PRISTINE files
def get_master_cv_pristine():
    cv_pristine_all = [] # List of all CV pristine data frames

    # For each row, read CV file, and append to list
    for _, row in master.iterrows():
        # Get cv file name
        cv_file_name = row["CV_Baseline "]
        
        # Skip if file name is nan
        if cv_file_name == np.nan:
            continue

        # Try reading file, skip if not found
        try:
            cv = pd.read_csv(f"CV/CV_PRISTINE/{cv_file_name}")
        except FileNotFoundError:
            continue
        
        # Add file_name column for joining purposes
        cv["file_name"] = cv_file_name

        # Append this DataFrame to list
        cv_pristine_all.append(cv)

    # Convert lists to a concatenation of all their contents
    cv_pristine_all = pd.concat(cv_pristine_all)

    # Join master with cf_pristine_all
    master_cv_pristine = master.merge(
        cv_pristine_all,
        left_on="CV_Baseline ", right_on="file_name",
        how="inner"
    )

    # The file names are no longer needed
    master_cv_pristine.drop(columns=["file_name", "Current"], inplace=True)

    return master_cv_pristine

# Will return a concatenation of all CF files. This includes exposed files,
# which are not in master_cf_pristine because the column is empty in master list
def get_cf():
    return

# Will return a concatenation of all CV files
def get_cv():
    return
