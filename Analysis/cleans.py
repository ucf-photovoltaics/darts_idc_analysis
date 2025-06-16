# Contains functions that produce cleaned and joined versions of the data. Feel
# free to add any functions to this file, and use any functions from here.

import pandas as pd
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

#-----------------------------------------------------------------------------------
# convert columns to the correct data type
master["Voltage"]=master["Voltage"].astype(int)
# add more here if needed


# Get a DataFrame that is the merging of the master data and all the
# CurrentTime files. Each row represents one current measurement at a given
# time, and it has data about the sensor, solution, etc. I used this to easily
# plot current vs time.
def get_master_current_time():
    # Join Data --------------------------------------------------------------------
    current_time_all = [] # Will be a concatenation of all currentTime csv files

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

master.reset_index(drop=True)
print(master)
