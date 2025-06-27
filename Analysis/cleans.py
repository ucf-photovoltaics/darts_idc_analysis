# Contains functions that produce cleaned and joined versions of the data. Feel
# free to add any functions to this file, and use any functions from here.

import reads
import pandas as pd
import numpy as np
import os
import typing
import cv2

# Internal helper function to get a dendrite score of a sensor image, given a
# pristine and exposed sensor
def _get_dendrite_score(pristine_file, exposed_file):
    # Skip if files are nan
    if pristine_file == np.nan or exposed_file == np.nan:
        return np.nan
    # Skip if files don't exist
    if not os.path.isfile(f"Imgscans_PRISTINE_sensors/{pristine_file}") or\
        not os.path.isfile(f"Imgscans_EXPOSED_sensors/{exposed_file}"):
        return np.nan
    
    # Read images
    pristine_image = cv2.imread(f"Imgscans_PRISTINE_sensors/{pristine_file}")
    exposed_image = cv2.imread(f"Imgscans_EXPOSED_sensors/{exposed_file}")

    # RGB analysis
    # TODO Replace np.mean with actual RGB analysis - Annabel
    score = np.mean(exposed_image)

    return score

# Get the cleaned master data
def get_master():
    # Read in data
    master = reads.get_master()

    # Cleans -------------------------------------------------------------------

    # Convert columns to the correct data type
    master["Voltage"] = pd.to_numeric(master["Voltage"], errors="coerce")
    master["Pattern"] = pd.to_numeric(master["Pattern"], errors="coerce")
    # TODO Do this for every column

    # Drop duplicate indices
    master = master[~master.index.duplicated(keep="first")]
    # drop rows with NaN
    master.dropna(subset=["Solution", "Voltage", "Pattern"], inplace=True)
    # drop columns and rows that are not being used
    master = master[(master["Status"] != "Not started") & (master["Status"] != "In progress")]
    # drop columns that are unnecessary
    master = master.drop(["Location", "Notes", "Tags"], axis=1)
    
    # Add image file names
    for file_name in os.listdir("Imgscans_PRISTINE_sensors"):
        batch, pattern, id, _, sensor = file_name.split(".")[0].split("_")
        pattern = int(pattern)
        mask = (master["Pattern"] == pattern) & (master["Sensor"] == sensor)
        master.loc[mask, "Image_PRISTINE"] = file_name
    for file_name in os.listdir("Imgscans_EXPOSED_sensors"):
        batch, pattern, id, _, sensor = file_name.split(".")[0].split("_")
        board_id = "_".join([batch, pattern, id])
        if (board_id, sensor) in master.index:
            master.loc[(board_id, sensor), "Image_EXPOSED"] = file_name
    # TODO Remove CV, CF, and CurrentTime file names from the stored CSV. Add
    # code here to populate those columns automatically

    # Calculate dendrite score
    master["Dendrite Score"] = master.apply(lambda row: _get_dendrite_score(row["Image_PRISTINE"], row["Image_EXPOSED"]), axis=1)

    return master

# Get a DataFrame that is the merging of the master data and all the
# CurrentTime files. Each row represents one current measurement at a given
# time, and it has data about the sensor, solution, etc.
def get_master_current_time():
    master = get_master()

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

# Returns the master merged with all CF files, or all CV files. An "Age" column
# is added to differentiate "PRISTINE" vs "EXPOSED"
def get_master_cf_or_cv(cf_or_cv: typing.Literal["CF", "CV"]):
    master = get_master()

    df_all = [] # List of all DataFrames, either cf or cv, has an Age column

    # Populate df_all with both ages
    for age in ["PRISTINE", "EXPOSED"]:
        # For each row, read file, and append to list
        for _, row in master.iterrows():
            # Get file name
            baseline_or_post = "Baseline" if age == "PRISTINE" else "Post"
            file_name = row[f"{cf_or_cv}_{baseline_or_post}"]
            
            # Skip if file name is nan
            if file_name == np.nan:
                continue

            # Try reading file, skip if not found
            try:
                df = pd.read_csv(f"{cf_or_cv}/{cf_or_cv}_{age}/{file_name}")
            except FileNotFoundError:
                continue
            
            # Add Age column to differentiate PRISTINE and EXPOSED
            df["Age"] = age

            # Add File Name column for joining purposes
            df["File Name"] = file_name

            # Append this DataFrame to list
            df_all.append(df)

    # Convert lists to a concatenation of all their contents
    df_all = pd.concat(df_all, ignore_index=True)
    
    # Join master with baseline files
    master_pristine = master.merge(
        df_all,
        left_on=f"{cf_or_cv}_Baseline",
        right_on="File Name",
        how="inner"
    )
    # Join master with post files
    master_exposed = master.merge(
        df_all,
        left_on=f"{cf_or_cv}_Post",
        right_on="File Name",
        how="inner"
    )

    # Concat both merges into the result
    master_cf_or_cv = pd.concat([master_pristine, master_exposed])

    # The file names are no longer needed
    master_cf_or_cv.drop(columns=["File Name", f"{cf_or_cv}_Baseline", f"{cf_or_cv}_Post"], inplace=True)

    return master_cf_or_cv

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
