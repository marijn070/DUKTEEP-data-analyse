import datetime
import glob
from datetime import timedelta

from config import DUKTEEP_LINK, FACE_PATHS_WITH_NAMES, VIDEO_DIR
from db import get_connection
from face_recognition.registration import register_video
from face_recognition.search import find_faces
from video.downloader import download_channel
from video.metadata import get_duration


def main():
    # get the videos from the channel
    download_channel(DUKTEEP_LINK, VIDEO_DIR)

    # get all the mp4 files
    mp4_files = glob.glob(f"{VIDEO_DIR}/*.mp4")
    total_playtime: timedelta = sum((get_duration(f) for f in mp4_files), timedelta())
    # print stats (total videos, total length)
    print(f"Totaal aantal videos: {len(mp4_files)}")
    print(f"Totale lengte: {total_playtime}")

    with get_connection() as conn:
        total_videos = len(mp4_files)

        for i, mp4_file in enumerate(mp4_files, 1):
            print(f"Processing video {i}/{total_videos}: {mp4_file}")
            register_video(mp4_file, conn)

        face_paths_with_names = FACE_PATHS_WITH_NAMES

        print("Finding dukteepers...")
        df = find_faces(conn, face_paths_with_names)

        print("Saving results...")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        df.to_parquet(f"data/dukteepers_{timestamp}.parquet")


if __name__ == "__main__":
    main()
