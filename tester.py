"""
This file is only used for testing purposes!
"""

from libraries.iw_handler import IWHandler
import os
import pandas as pd

def main():
    if not os.path.isfile("data/data1.xlsx"):
        raise FileNotFoundError()
    if not os.path.isfile("data/data1.xlsx"):
        raise FileNotFoundError()
    df1 = pd.read_excel("data/data1.xlsx")
    df2 = pd.read_excel("data/data2.xlsx")

    handler = IWHandler()
    handler.load_data(df1, df2)
    print("*"*10)
    print(handler.compute())


if __name__ == "__main__":
    main()