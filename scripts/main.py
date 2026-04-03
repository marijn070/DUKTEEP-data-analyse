import contextlib
import glob
import os
from datetime import timedelta
from pathlib import Path

import cv2
import psycopg
from deepface import DeepFace
from downloader import download_channel
from frame_sampler import sample_frames_with_info
from tqdm import tqdm

DUKTEEP_LINK: str = "https://www.youtube.com/@dukteep"
REGISTERED_VIDEOS_FILE = "registered_videos.txt"


def get_duration(f) -> timedelta:
    cap = cv2.VideoCapture(f)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)

    return timedelta(seconds=frames / fps) if fps > 0 else timedelta(seconds=0)


def get_existing_image_names(conn):
    """Load set of existing image names from the database"""
    with conn.cursor() as cur:
        cur.execute("SELECT img_name FROM embeddings")
        return set(row[0] for row in cur.fetchall())


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


def main():
    # get the videos from the channel
    download_channel(DUKTEEP_LINK)

    # get all the mp4 files
    mp4_files = glob.glob("videos/*.mp4")
    total_playtime: timedelta = sum((get_duration(f) for f in mp4_files), timedelta())

    # print stats (total videos, total length)
    print(f"Totaal aantal videos: {len(mp4_files)}")
    print(f"Totale lengte: {total_playtime}")

    dukteep_faces = [
        "known_faces/marijn.png",
        "known_faces/angela.jpg",
        "known_faces/keon.png",
        "known_faces/mees.png",
    ]

    with psycopg.connect("postgresql://postgres:postgres@localhost:5432/postgres") as conn:
        # registered_videos = load_registered_videos()
        total_videos = len(mp4_files)

        for i, mp4_file in enumerate(mp4_files, 1):
            print(f"Processing video {i}/{total_videos}: {mp4_file}")


if __name__ == "__main__":
    main()
