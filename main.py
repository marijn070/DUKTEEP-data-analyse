import contextlib
import glob
import os
from datetime import timedelta
from pathlib import Path

import cv2
import pandas as pd
from deepface import DeepFace
from tqdm import tqdm

from config import DUKTEEP_LINK
from db import get_connection, get_existing_image_names
from video.downloader import download_channel
from video.sampler import sample_frames_with_info


def get_duration(f) -> timedelta:
    cap = cv2.VideoCapture(f)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)

    return timedelta(seconds=frames / fps) if fps > 0 else timedelta(seconds=0)


def register_video(mp4_file, conn):
    total, frames = sample_frames_with_info(mp4_file, interval=1.0)

    existing = get_existing_image_names(conn)
    new_inserted = 0

    for timestamp, frame in tqdm(frames, total=total):
        img_name = f"{Path(mp4_file).stem}_{timestamp:.2f}s"

        # check if already registered
        if img_name in existing:
            continue
        try:
            # DeepFace.register prints to stdout, redirect to devnull
            with open(os.devnull, "w") as f, contextlib.redirect_stdout(f):
                DeepFace.register(
                    frame,
                    img_name=f"{Path(mp4_file).stem}_{timestamp:.2f}s",
                    connection=conn,
                    enforce_detection=False,
                )
            new_inserted += 1
        except Exception as e:
            tqdm.write(f"Error processing {mp4_file} at timestamp {timestamp:.2f}s: {e}")

    print(
        f"Registered {new_inserted} frames from {mp4_file}, ({total - new_inserted} already registered)"
    )


def find_dukteepers(conn, face_paths_with_names):

    names = list(face_paths_with_names.keys())
    paths = list(face_paths_with_names.values())

    dfs = DeepFace.search(
        img=paths,
        connection=conn,
    )

    def process_df(df, name):
        df = df.copy()

        df[["date_str", "rest"]] = df["img_name"].str.split(" - ", expand=True)
        df["date"] = pd.to_datetime(df["date_str"], format="%Y%m%d").dt.date

        df[["video", "timestamp_str"]] = df["rest"].str.split("_", expand=True)

        df["timestamp"] = df["timestamp_str"].str.replace("s", "", regex=False).astype(float)

        df["dukteeper"] = name

        return df[["date", "video", "timestamp", "dukteeper"]]

    processed = [process_df(df, name) for df, name in zip(dfs, names)]

    return pd.concat(processed, ignore_index=True)


def main():
    # get the videos from the channel
    download_channel(DUKTEEP_LINK)

    # get all the mp4 files
    mp4_files = glob.glob("videos/*.mp4")

    total_playtime: timedelta = sum((get_duration(f) for f in mp4_files), timedelta())

    # print stats (total videos, total length)
    print(f"Totaal aantal videos: {len(mp4_files)}")
    print(f"Totale lengte: {total_playtime}")

    with get_connection() as conn:
        total_videos = len(mp4_files)

        for i, mp4_file in enumerate(mp4_files, 1):
            print(f"Processing video {i}/{total_videos}: {mp4_file}")
            register_video(mp4_file, conn)

        face_paths_with_names = {
            "marijn": "known_faces/marijn.png",
            "koen": "known_faces/koen.png",
            "angela": "known_faces/angela.png",
            "koen": "known_faces/koen.png",
        }

        print("Finding dukteepers...")

        df = find_dukteepers(conn, face_paths_with_names)


if __name__ == "__main__":
    main()
