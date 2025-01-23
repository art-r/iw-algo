"""
This is an alternative way of running
the libraries/iw_handler module

app.py targets a webapp, where this can be run directly from
a laptop without the need of a web app
"""

import os

from libraries.iw_handler import IWHandler

###################################
# CONFIGURE THIS
# path to the input file
INPUT_DATA = "data/danish.xlsx"

# name of the output file (should end with .xlsx)
OUTPUT_NAME = "groups.xlsx"
###################################


def main(input_data: str, outpath: str):
    """
    The main entry point
    Arguments:
    - inputData (str): path to the input file
    """
    if not os.path.isfile(input_data):
        raise FileNotFoundError(f"Provided path is :'{input_data}'")
    handler = IWHandler()
    handler.load_data(input_data)
    print("Loaded data successfully")
    print("Started the process for group creation...")
    df = handler.compute()
    print("Created groups successfully")

    df.to_excel(outpath)
    print(f"Saved overall overview to '{outpath}'")

    # save also sorted by buddy group
    # will be done in extra script
    # this allows to first run assign_remaining!
    # df = df.sort_values(by=["buddy group"])
    # outpath = f"{outpath.split('.')[0]}-BUDDYGROUPS.xlsx"
    # df.to_excel(outpath)
    # print(f"Saved overview sorted by buddy groups to '{outpath}'")


if __name__ == "__main__":
    main(INPUT_DATA, OUTPUT_NAME)
