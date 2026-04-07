import os
import pickle
import sys

import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def process_df(df, name):
    df = df.copy()

    df[["date_str", "rest"]] = df["img_name"].str.split(" - ", expand=True)
    df["date"] = pd.to_datetime(df["date_str"], format="%Y%m%d")
    df[["video", "timestamp_str"]] = df["rest"].str.split("_", expand=True)
    df["timestamp"] = pd.to_timedelta(df["timestamp_str"].str.rstrip("s").astype(float), unit="s")
    df["person_name"] = name

    return df[
        [
            "date",
            "video",
            "timestamp",
            "person_name",
            "model_name",
            "detector_backend",
            "search_method",
        ]
    ]


if __name__ == "__main__":
    marijn, angela, koen, mees = pickle.load(open("dfs.pkl", "rb"))

    print(marijn.columns)

    marijn = process_df(marijn, "marijn")
    angela = process_df(angela, "angela")
    koen = process_df(koen, "koen")
    mees = process_df(mees, "mees")

    df = pd.concat([marijn, angela, koen, mees])

    df.to_parquet("old_dbs.parquet")

    print(marijn)
