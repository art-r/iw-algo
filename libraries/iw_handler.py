"""
The core file handling all logic

Notes:
Class to preserve parsed files

1. load config file and read vals
2. compute amount of categories
3. parse file1 & file2
4. assign students to categories (preserve order, oldest on top)
5. assign students to extra-categories based on constraints
"""

import json

import pandas as pd


class IWHandler:
    """
    The main class that implements all the logic
    """

    def __init__(self):
        self.__config = self.__read_config()
        self.__c_amount = len(self.__config["categories"].keys())
        self.__prev_data = False
        self.__data = None
        self.__ext_data = None

    def __read_config(self):
        """
        Internal helper function to read the config file
        """
        try:
            conf_path = "../config.json"
            with open(conf_path, mode="r", encoding="utf-8") as in_file:
                config = json.load(in_file)
            return config
        except json.JSONDecodeError as exc:
            print(f"Tried to read {conf_path}")
            raise exc

    def load_data(self, data, extData):
        """
        Internal helper function parse the provided excel data with pandas
        """
        self.__data = pd.read_excel(data, header=0)
        self.__ext_data = pd.read_excel(extData, header=0)
        self.__prev_data = True

    def prev_data_exists(self):
        """
        Public function to determine if previous data is available
        """
        return self.__prev_data

    def __check_easy_case(self):
        """
        Internal helper function to check if the easy case applies.
        This means that:
            - all categories have no limit OR
            - the amount of people that chose a category in their 1st pref < category limit
        """
        # check if all have no limit
        no_limit = True
        for c_info in self.__config["categories"].values():
            if c_info[0] != -1:
                # Found one category with a limit
                no_limit = False
                break

        # if all have no limit stop already here
        if no_limit:
            return True

        # compare the limits
        all_below_limit = True
        for c_name, c_info in self.__config["categories"].items():
            df_key = f"{self.__config["prefMainK"]}1"
            # no limit for this category, so ignore it
            if c_info[0] == -1:
                continue
            # category with a limit, so compare
            if self.__data[self.__data[df_key] == c_name][df_key].count() > c_info[0]:
                # Found one category where the amount of people that selected it
                # is larger than the category capacity
                all_below_limit = False
                break
        return all_below_limit

    def compute(self):
        """
        Public function that runs the core logic
        """
        df = pd.DataFrame()
        # Name - Student Number - Assignment
        df.columns = [
            self.__config["nameK"],
            self.__config["sidK"],
            "Assigned Category",
            "Special Group",
        ]

        # Easy case: all can get their 1st preference
        if self.__check_easy_case():
            df[self.__config["nameK"]] = self.__data[self.__config["nameK"]]
            df[self.__config["sidK"]] = self.__data[self.__config["sidK"]]
            pref_key = f"{self.__config["nameK"]}1"
            df[self.__config["Assigned Category"]] = self.__data[pref_key]
        else:
            # create a copy of original df
            df_org = self.__data.copy(True)

            # not everybody can get their 1st preference!
            # assign based upon first come, first serve (FCFS)
            # filter df and then assign up to capacity
            # do this for every category
            # then assign non-assigned based upon 2nd pref if capacity allows
            # if not try 3rd pref, 4th pref etc. and else assign to UNASSIGNABLE

            # the amount of categories
            c_amount = len(self.__config["categories"].keys())

            # iterate through all categories and assign
            for i in range(1, c_amount + 1):
                pref_key = f"{self.__config["prefMainK"]}{i}"
                for c, c_info in self.__config["categories"].items():
                    # category with no limit
                    if c_info[0] == -1:
                        # assign directly since this category has no limit
                        df[self.__config["nameK"]] = df_org[df_org[pref_key] == c][
                            self.__config["nameK"]
                        ]
                        df[self.__config["sidK"]] = df_org[df_org[pref_key] == c][
                            self.__config["sidK"]
                        ]
                        df[self.__config["Assigned Category"]] = df_org[
                            df_org[pref_key] == c
                        ][pref_key]
                        # TODO: remove the assigned people from the original df to not reassign
                    else:
                        # category with a limit
                        # first check if limit is already exceeded
                        taken_spots = df[df["Assigned Category"] == c].count()
                        if taken_spots < c_info[0]:
                            # still space
                            # the remaining spots
                            rem_spots = c_info[0] - taken_spots
                            # the people that get a spot
                            df[self.__config["nameK"]] = df_org[df_org[pref_key] == c][
                                self.__config["nameK"]
                            ][:rem_spots]
                            df[self.__config["sidK"]] = df_org[df_org[pref_key] == c][
                                self.__config["sidK"]
                            ][:rem_spots]
                            df[self.__config["Assigned Category"]] = df_org[
                                df_org[pref_key] == c
                            ][pref_key][:rem_spots]
                            # TODO: remove the assigned people from the original df to not reassign
            # now check if everybody was assigned
            # this means counting the remaining people in the original df
            if df_org.count() > 0:
                # unassignable people
                df[self.__config["nameK"]] = df_org[self.__config["nameK"]]
                df[self.__config["sidK"]] = df_org[self.__config["sidK"]]
                df[self.__config["Assigned Category"]] = "UNASSIGNABLE"

        # handle the sub groups for the special categories
        # filter for special categories
        # lookup the respective buddy group
        for c, c_info in self.__config["categories"].keys():
            # skip non-special categories
            if c_info[1] is False:
                continue
            # create new df with full information
            df_org = self.__data.copy(True)
            # TODO: merge info with extra data for buddy groups
            # df.merge()
            # TODO: create sub groups
            # (https://stackoverflow.com/a/73738016)
        return df
