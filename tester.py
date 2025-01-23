"""
This file is only used for testing purposes!
"""

import os
import pandas as pd

def main():
    if not os.path.isfile("data/danish.xlsx"):
        raise FileNotFoundError()

    df = pd.read_excel("data/danish.xlsx")
    col = "🟠Classify your priority on the following workshops, we will try to fit you into what you preferred! (You can find the descriptions of each workshop in the description of the forms and also on you..."
    categories_df = pd.DataFrame(df[col].str.split(";", expand=True).values, columns=["pref1", "pref2", "pref3", "pref4", "ext"])
    categories_df.drop("ext", axis=1, inplace=True)
    # print(categories_df)
    df = pd.concat([df,categories_df], axis=1)
    print(df[["Name", "pref1", "pref2", "pref3", "pref4"]])

if __name__ == "__main__":
    main()