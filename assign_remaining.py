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
pd.options.mode.chained_assignment = None 

###################################
# CONFIGURE THIS
# path to the input file containing all students (or remaining students)
INPUT_DATA = "data/danish.xlsx"

# name of the input file that contains all groups (will be updated)
GROUPS_FILE = "groups1.xlsx"

# name of the output file (should end with .xlsx)
OUTPUT_NAME = "remaining_assigned.xlsx"

# path to the config file
CONFIG = "config.json"
###################################

def validate_file(path, name):
    """
    Helper function to validate a file exists
    """
    if not os.path.isfile(path):
        print(f"FATAL ERROR: Could not find {name}")
        print(f"Provided path is: {path}")
        sys.exit(1)

def assign_rand_group(rng, av_space: dict):
    """
    Helper function assign a person to a random group
    """
    # determine still available category
    choices = [x for x,y in av_space.items() if y > 0]
    assigned_group = None
    if len(choices) != 0:
        # return a randomly chosen choice
        rand_selec = rng.integers(0,len(choices))
        assigned_group = choices[rand_selec]
        av_space[assigned_group] -= 1
    return assigned_group, av_space

def main(conf_path: str, main_file: str, group_file: str, output_file: str):
    """
    The main part of this script
    """
    validate_file(conf_path, "config file")
    try:
        with open(conf_path, mode="r", encoding="utf-8") as in_file:
            config = json.load(in_file)
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

    if missing_df.shape[0] == 0:
        print("Did not find any missing students")
        sys.exit(0)

    # validate if there is even still space in any workshop
    # assume first that there will be not enough space
    # track also how much space exactly is left per category
    all_assignable = False
    total_space = 0
    av_space = {}
    for c, c_info in config["categories"].items():
        taken_spots = group_df[group_df["Assigned Category"] == c][config["nameK"]].count()
        rem_spots = c_info[0] - taken_spots
        total_space += rem_spots
        av_space[c] = rem_spots
        if total_space >= missing_df[config["nameK"]].count():
            # there is enough space
            all_assignable = True

    if total_space == 0:
        print("Error: There is no space left in any workshop!")
        print("Exiting now")
        sys.exit(0)

    if all_assignable is False:
        print("Info: Not all students will be assignable!")
        print(f"There is only {total_space} spots")

    # now assign randomly based upon space
    rng = np.random.default_rng()
    assigned_categories = []
    assigned_subgroups = []
    # categories that require subgroups
    c_with_subgroups = [c for c,info in config["categories"].items() if info[1]]

    for _, row in missing_df.iterrows():
        category, av_space = assign_rand_group(rng, av_space)
        if category is None:
            category = "UNASSIGNABLE"
            subgroup = "N/A"
        elif category in c_with_subgroups:
            # also choose a random subgroup from the amount of available subgroups
            # note that this might result in some subgroups having a larger
            # amount of students than wanted!
            subgroup = rng.integers(1,config["categories"][category][2])
        else:
            subgroup = "N/A"
        assigned_categories.append(category)
        assigned_subgroups.append(subgroup)

    missing_df["Assigned Category"] = np.array(assigned_categories)
    missing_df["Assigned Subgroup"] = np.array(assigned_subgroups)
    print("Done")
    cols = [
            config["nameK"],
            config["sidK"],
            config["buddyK"],
            "Assigned Category",
            "Assigned Subgroup",
        ]
    # rename the buddy column to match the output of the iw_handler file
    missing_df = missing_df[cols]
    missing_df.rename(columns={config["buddyK"] : 'buddy group'}, inplace=True)
    missing_df.to_excel(output_file)
    # merge the output
    group_df = pd.concat([group_df, missing_df])
    # drop a potential new unnamed 0 column
    group_df.drop(["Unnamed: 0", "index"], axis=1, inplace=True, errors="ignore")
    # reset index
    group_df.reset_index(inplace=True)
    # sort
    group_df = group_df.sort_values(by=["Assigned Category", "Assigned Subgroup"])
    group_df.to_excel(group_file)

if __name__ == "__main__":
    main(CONFIG, INPUT_DATA, GROUPS_FILE, OUTPUT_NAME)
