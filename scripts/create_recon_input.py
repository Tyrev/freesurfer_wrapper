"""Script to create recon input table

This script creates an input table based on the directory organization
of the image files. 

Please edit the **PATH_PATTERN** variable with the appropriate
pathname pattern to find each file.

This file can also be imported as a module and contains the following
functions:

    * create_input_file - creates the input table.

"""

from glob import glob
import pandas as pd

# Pathname pattern to find each file
# * is a wildcard standing for "any string of characters"
# ADNI/ALL_SUBJECTS/MP-RAGE/ALL_TIME_POINTS/SESSION_ID/FIRST_DCM_FILE
PATH_PATTERN = "ADNI/*/MP-RAGE/*/*/*_1_*"

def create_input_file(path_pattern: str):
    """
    Creates a two column text file to be used as input for the main script recon command.
    First column: unique ID (combines SUBJECT ID and SESSION ID).
    Second column: path to DICOM file.

    Parameters
    ----------
    path_pattern : str
        Glob pathname pattern to find each DICOM file.

    Returns
    -------
    None

    """
    files = glob(path_pattern)
    data = [[f"{file.split('/')[1]}_{file.split('/')[-2]}", file] for file in files]
    table = pd.DataFrame(data)
    table.to_csv("recon_input.txt", sep="\t", index=False, header=False)

if __name__ == '__main__':
    create_input_file(PATH_PATTERN)