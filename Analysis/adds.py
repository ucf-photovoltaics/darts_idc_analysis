# This is the second stage of the pipeline. Additions are made to the data, such
# as new columns, and joins. Data removal should be minimal here, to prevent
# loss of useful data.

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
    
    # Add image file names
    for file_name in os.listdir("Imgscans_PRISTINE_sensors"):
        # Get components
        batch, pattern, id, _, sensor = file_name.split(".")[0].split("_")
        pattern = int(pattern)
        # Mask only where pattern and sensor match
        mask = (master["Pattern"] == pattern) & (master["Sensor"] == sensor)
        # Store the file name using the mask
        master.loc[mask, "Image_PRISTINE"] = file_name
    for file_name in os.listdir("Imgscans_EXPOSED_sensors"):
        # Get components
        batch, pattern, id, _, sensor = file_name.split(".")[0].split("_")
        board_id = "_".join([batch, pattern, id])
        # Mask only where board ID and sensor match
        mask = (master["Board ID"] == board_id) & (master["Sensor"] == sensor)
        # Store the file name using the mask
        master.loc[mask, "Image_EXPOSED"] = file_name
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
        # Get the current_in value, which could be a float or file name
        current_in = row["Current"]

        # Read file, and skip if result is None
        current_time = reads.get_current_time(current_in)
        if current_time is None:
            continue

        # Add file_name column for joining purposes
        current_time["File Name"] = current_in

        # Append this current_time to current_time_all
        current_time_all.append(current_time)

    # Convert current_time_all, (a list), to a concatenation of all its contents
    current_time_all = pd.concat(current_time_all)

    # Join master with current_time_all
    master_current_time = master.merge(
        current_time_all,
        left_on="Current", right_on="File Name",
        how="inner"
    )

    # The file names are no longer needed
    master_current_time.drop(columns=["File Name", "Current"], inplace=True)

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
            
            # Read df, skipping if result is None
            df = reads.get_cf_or_cv(file_name)
            if df is None:
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
