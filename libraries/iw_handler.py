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
            conf_path = "config.json"
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
        try:
            self.__data = pd.read_excel(data, header=0)
            self.__ext_data = pd.read_excel(extData, header=0)
        except ValueError:
            # passing potentially an already parsed dataframe
            self.__data = data
            self.__ext_data = extData
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
        Public function that runs the core logic.
        The assignment of students goes as follows:
        - (Easy case) the categories are chosen less then their limits
        ==> all can get their 1st preference
        - (Else) Assign up to remaining limit for the 1st preference
        while considering the first-come-first-serve logic
        - Then go through the remaining unassigned students
        and handle their 2nd,3rd,...
        If at the end no category has enough space the remaining students
        are assigned to category "UNASSIGNED" to mark that they cant be assigned

        Then the special categories are handled where sub-groups need to be created
        """
        # Name - Student Number - Assignment
        cols = [
            self.__config["nameK"],
            self.__config["sidK"],
            "Assigned Category",
            "Special Group",
        ]
        df = pd.DataFrame(columns=cols)

        # Easy case: all can get their 1st preference
        if self.__check_easy_case():
            df[self.__config["nameK"]] = self.__data[self.__config["nameK"]]
            df[self.__config["sidK"]] = self.__data[self.__config["sidK"]]
            pref_key = f"{self.__config["prefMainK"]}1"
            df["Assigned Category"] = self.__data[pref_key]
        else:
            # create a copy of original df
            df_org = self.__data.copy(True)

            # the amount of categories
            c_amount = len(self.__config["categories"].keys())
            # iterate through all categories and assign
            for i in range(1, c_amount + 1):
                pref_key = f"{self.__config["prefMainK"]}{i}"
                for c, c_info in self.__config["categories"].items():
                    # category with no limit
                    if c_info[0] == -1:
                        # assign directly since this category has no limit
                        df = pd.concat(
                            [df, df_org[df_org[pref_key] == c]], ignore_index=True
                        )[cols]

                        df["Assigned Category"] = df["Assigned Category"].fillna(c)
                        df_org = df_org[
                            ~df_org[self.__config["sidK"]].isin(
                                df[self.__config["sidK"]]
                            )
                        ]
                    else:
                        # category with a limit
                        # first check if limit is already exceeded
                        taken_spots = df[df["Assigned Category"] == c][
                            "Assigned Category"
                        ].count()
                        if taken_spots < c_info[0]:
                            print("Still space: ", taken_spots)
                            # still space
                            # the remaining spots
                            rem_spots = c_info[0] - taken_spots
                            # the people that get a spot
                            # print(df_org[df_org[pref_key] == c][:rem_spots])
                            df = pd.concat(
                                [df, df_org[df_org[pref_key] == c][:rem_spots]],
                                ignore_index=True,
                            )[cols]
                            df["Assigned Category"] = df["Assigned Category"].fillna(c)
                            df_org = df_org[
                                ~df_org[self.__config["sidK"]].isin(
                                    df[self.__config["sidK"]]
                                )
                            ]
            # now check if everybody was assigned
            # this means counting the remaining people in the original df
            if df_org.shape[0] > 0:
                # unassignable people
                df = pd.concat([df, df_org], ignore_index=True)[cols]
                df["Assigned Category"] = df["Assigned Category"].fillna("UNASSIGNABLE")

        # handle the sub groups for the special categories
        # filter for special categories
        # lookup the respective buddy group
        for c, c_info in self.__config["categories"].items():
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
