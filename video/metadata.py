from datetime import timedelta

import cv2


def get_duration(f) -> timedelta:
    cap = cv2.VideoCapture(f)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)

    return timedelta(seconds=frames / fps) if fps > 0 else timedelta(seconds=0)
