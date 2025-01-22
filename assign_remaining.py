"""
The purpose of this script is to assign the
students that have not signed up for any workshop to random
workshops that still have space

It wil read in all students and compare it to the groups file
to determine which students have not yet been assigned

Then it will assign them randomly to a workshop that still has space
and afterwords update the groups file AND additionally output
a file that contains the just assigned students
"""
import json
import os
import sys

import numpy as np
import pandas as pd

###################################
# CONFIGURE THIS
# path to the input file containing all students (or remaining students)
INPUT_DATA = "data/data1.xlsx"

# name of the input file that contains all groups (will be updated)
GROUPS_FILE = "groups.xlsx"

# name of the output file (should end with .xlsx)
OUTPUT_NAME = "remaining.xlsx"
###################################

def validate_file(path, name):
    if not os.path.isfile(path):
        print(f"FATAL ERROR: Could not find {name}")
        print(f"Provided path is: {path}")
        sys.exit(1)

def assign_rand_group(rng, av_space):
    # determine still available category
    choices = [x for x,y in av_space.items() if y > 0]
    # return a randomly chosen choice
    return choices[rng.integers(0,len(choices))]

def main(conf_path: str, main_file: str, group_file: str):
    """
    The main part of this script
    """
    validate_file(conf_path, "config file")
    try:
        with open(conf_path, mode="r", encoding="utf-8") as in_file:
            config = json.load(in_file)
        return config
    except json.JSONDecodeError as exc:
        print(f"Tried to read {conf_path}")
        raise exc

    validate_file(main_file, "main input (containing all student or remaining student info)")
    validate_file(group_file, "group input (containing all assigned group info)")

    df = pd.read_excel(main_file, header=0)
    group_df = pd.read_excel(group_file, header=0)

    # determine the missing students
    assigned_ids = group_df[config["sidK"]].values
    missing_df = df[~df[config["sidK"]].isin(assigned_ids)]

    # validate if there is even still space in any workshop
    # assume first that there will be not enough space
    # track also how much space exactly is left per category
    all_assignable = False
    total_space = 0
    av_scape = {}
    for c, c_info in config["categories"].items():
        taken_spots = group_df[group_df["Assigned Category"] == c][config["nameK"]].count()
        rem_spots = c_info[0] - taken_spots
        total_space += rem_spots
        av_scape[c] = rem_spots
        if total_space >= missing_df[config["nameK"]].count():
            # there is enough space
            all_assignable = True
            break

    if total_space == 0:
        print("Error: There is not space left in any workshop!")
        print("Exiting now")
        sys.exit(0)

    if all_assignable is False:
        print("Info: Not all students will be assignable!")

    # now assign randomly based upon space
    rng = np.random.default_rng()
    choices = len(config["categories"].keys())
    missing_df["Assigned Category"] = ""
    
    for _, row in missing_df.iterrows():
        pass