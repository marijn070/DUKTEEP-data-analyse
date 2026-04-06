import pandas as pd
from deepface import DeepFace

from config import DATABASE_TYPE, MODEL_NAME


def find_faces(conn, face_paths_with_names) -> pd.DataFrame:
    names = list(face_paths_with_names.keys())
    paths = list(face_paths_with_names.values())

    dfs = DeepFace.search(
        img=paths,
        connection=conn,
        database_type=DATABASE_TYPE,
        model_name=MODEL_NAME,
        # search_method="ann",
    )

    processed = [process_df(df, name) for df, name in zip(dfs, names)]

    return pd.concat(processed, ignore_index=True)


def process_df(df, name):
    df = df.copy()

    df[["date_str", "video", "timestamp_str"]] = df["img_name"].str.split("__", n=2, expand=True)
    df["date"] = pd.to_datetime(df["date_str"], format="%Y%m%d")
    df["timestamp"] = pd.to_timedelta(df["timestamp_str"].astype(float), unit="s")
    df["person_name"] = name

    return df[["date", "video", "timestamp", "person_name"]]
