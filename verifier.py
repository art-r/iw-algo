"""
The purpose of this script is to verify the following properties
of the assigned groups:
- amount of students per workshop
- amount of subgroups per workshop (if applicable)
- amount of unassigned students (marked with "UNASSIGNED")
"""

import os
import sys
import json

import pandas as pd

###################################
# CONFIGURE THIS
# path to the config file
CONFIG_FILE = "config.json"

# name of the input file that contains all groups (will be updated)
GROUPS_FILE = "groups.xlsx"
###################################


def validate_file(path, name):
    """
    Helper file to check if a given file exists
    """
    if not os.path.isfile(path):
        print(f"FATAL ERROR: Could not find {name}")
        print(f"Provided path is: {path}")
        sys.exit(1)


def main(conf_path, groups_path):
    """
    The main file of this script
    """
    validate_file(conf_path, "config file")
    validate_file(groups_path, "file containing the workshop data")

    try:
        with open(conf_path, mode="r", encoding="utf-8") as in_file:
            config = json.load(in_file)
    except json.JSONDecodeError as exc:
        print(f"Tried to read {conf_path}")
        raise exc

    df = pd.read_excel(groups_path, header=0)

    # check amount of unassigned students
    unassigned = df[df["Assigned Category"] == "UNASSIGNED"][config["nameK"]].count()
    if unassigned > 0:
        print("WARNING: There are unassigned students:")
        print("These are the students:")
        print(df[df["Assigned Category"] == "UNASSIGNED"][config["nameK"]])
        print("#" * 15)
    else:
        print(f"{df.shape[0]} assigned people in total")

    # check workshop statistics
    print("\nWorkshop information:")
    for c, c_info in config["categories"].items():
        # filter the df to the current category
        df_filter = df[df["Assigned Category"] == c]
        assigned_st = df_filter[config["nameK"]].count()
        above_limit = True if assigned_st > c_info[0] else False
        print(f"\n- {c}:")
        print(f"\t- {assigned_st} assigned people")
        if above_limit:
            print(f"\tWARNING!! This is above the configured limit of {c_info[0]}!!)")

        # subgroup check (but only if configured to have subgroups)
        if c_info[1]:
            amount_groups = len(df_filter["Assigned Subgroup"].unique())
            correct_amount = amount_groups == c_info[2]
            print(f"\t- There are {amount_groups} subgroups")
            if not correct_amount:
                print(
                    f"\tWARNING!! This differs from the configured amount ({c_info[2]})"
                )
        else:
            # check that nobody in this category has been assigned to a subgroup
            subgroup_ppl = df_filter[~df_filter["Assigned Subgroup"].isna()][
                config["nameK"]
            ].count()
            if subgroup_ppl > 0:
                print(
                    "\tWARNING - Found subgroups even despite not supposed to find them"
                )
                print(
                    f"\tThere are {subgroup_ppl} people in this category that have a subgroup"
                )
                print("\tThese are the people:")
                print(
                    df_filter[~df_filter["Assigned Subgroup"].isna()][config["nameK"]]
                )
                print("#" * 15)


if __name__ == "__main__":
    main(CONFIG_FILE, GROUPS_FILE)
