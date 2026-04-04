from pathlib import Path

from deepface import DeepFace
from tqdm import tqdm

from config import DATABASE_TYPE, MODEL_NAME, SAMPLE_INTERVAL
from db import get_existing_image_names
from video.sampler import sample_frames_with_info


def register_video(mp4_file, conn):
    total, frames = sample_frames_with_info(
        mp4_file,
        interval=SAMPLE_INTERVAL,
    )

    existing = get_existing_image_names(conn)
    new_inserted = 0

    for timestamp, frame in tqdm(frames, total=total):
        img_name = f"{Path(mp4_file).stem}_{timestamp:.2f}s"

        # check if already registered
        if img_name in existing:
            continue
        try:
            DeepFace.register(
                frame,
                database_type=DATABASE_TYPE,
                img_name=f"{Path(mp4_file).stem}__{timestamp:.2f}",
                connection=conn,
                enforce_detection=False,
                model_name=MODEL_NAME,
            )
            new_inserted += 1
        except Exception as e:
            tqdm.write(f"Error processing {mp4_file} at timestamp {timestamp:.2f}s: {e}")

    print(
        f"Registered {new_inserted} frames from {mp4_file}, ({total - new_inserted} already registered)"
    )
