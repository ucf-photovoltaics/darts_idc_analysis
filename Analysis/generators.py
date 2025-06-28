# A place for intensive code that cannot be reasonably ran each time the
# DataFrame is generated. This code should only be run occasionally when new
# data is added.

import reads
import cv2
import os

# Helper function used to generate a singular sensor image
def _gen_sensor_image(master_row, age):
    # Read cropped sensor image
    sensor_image = reads.get_sensor_image(master_row, age)
    # If image can't be read, skip
    if sensor_image is None:
        return
    
    # Get values to construct file name, and store file
    # Date isn't used yet because of dates missing in master
    #month, day, year = tuple(map(int, master_row["Date"].split("/")))
    file_name = f"{master_row["Board ID"]}_{"000" if age == "PRISTINE" else "001"}_{master_row["Sensor"]}.jpg"

    # Write to file
    cv2.imwrite(f"Imgscans_{age}_sensors/{file_name}", sensor_image)

# Generate the cropped sensor images and store them
def gen_sensor_images():
    master = reads.get_master()

    # Drop NaNs because these columns are needed for creating the file name
    master.dropna(subset=["Board ID", "Date", "Sensor"], inplace=True)

    # Set index to a unique sensor identifier
    master.set_index(["Board ID", "Sensor"], inplace=True, drop=False)
    master.sort_index(inplace=True)
    # Drop duplicate indices
    master = master[~master.index.duplicated(keep='first')]

    # Counter variable for printed progress
    generated = 0

    for pristine_file_name in os.listdir("Imgscans_PRISTINE_edited"):
        for sensor in ["U1", "U2", "U3", "U4"]:
            batch, pattern, id, _ = pristine_file_name.split("_")
            board_id = "_".join([batch, pattern, id])

            # Get master rows that match this file
            rows = master[(master["Board ID"] == board_id) & (master["Sensor"] == sensor)]
            # Skip if no master rows match
            if len(rows) == 0:
                continue
            # Generate image using the first found row
            _gen_sensor_image(rows.iloc[0], "PRISTINE")
            
            # Show progress
            generated += 1
            print(f"Images generated: {generated}")

    # For each row in master, generate the EXPOSED image if possible
    for _, row in master.iterrows():
        _gen_sensor_image(row, "EXPOSED")
        
        # Show progress
        generated += 1
        print(f"Images generated: {generated}")

# Run Area ---------------------------------------------------------------------
# Uncomment lines to run the generators

#gen_sensor_images()
