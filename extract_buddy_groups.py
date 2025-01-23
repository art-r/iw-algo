"""
This script creates a folder structure
that will then contain a per buddy group information
"""

import os
import sys

import pandas as pd

###################################
# CONFIGURE THIS
# name of the input file that contains all groups (will be updated)
GROUPS_FILE = "groups.xlsx"

# Name of the output dir
OUTPUT_DIR = "buddy_group_info"
###################################


def main(group_path, out_dir):
    """
    The main script
    """
    if not os.path.isfile(group_path):
        raise FileNotFoundError(f"Given path is: {group_path}")

    if os.path.isdir(out_dir):
        print("WARNING: Output dir already exists!!")
        print("Will abort")
        sys.exit(0)

    # create root dir
    os.makedirs(out_dir)

    # read data
    df = pd.read_excel(group_path, header=0)

    # sort by buddy group and reset index
    df.sort_values("buddy group", inplace=True)
    df.reset_index(inplace=True)

    # get the unique buddy group values
    buddy_groups = df["buddy group"].unique()

    # save the per buddy group info
    for group in buddy_groups:
        # create buddy group dir
        os.makedirs(os.path.join(out_dir, group))
        # save data
        file_path = os.path.join(out_dir, group, f"{group}-workshop.xlsx")
        df[df["buddy group"] == group].to_excel(file_path)

    print("Finished creating the folder structure")

    # save also an overall per buddy group file
    overall_name = f"{group_path.split('.xlsx')[0]}-per-buddygroups.xlsx"
    df.to_excel(overall_name)
    print(f"Saved also an overall file sorted per buddy groups to {overall_name}")


if __name__ == "__main__":
    main(GROUPS_FILE, OUTPUT_DIR)
