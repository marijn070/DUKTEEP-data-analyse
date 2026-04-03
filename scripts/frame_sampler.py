import math

import cv2


def sample_frames_with_info(video_path, interval=1.0):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    frame_interval = max(1, math.ceil(fps * interval))
    total_samples = math.ceil(total_frames / frame_interval)

    def generator():
        frame_id = 0
        while frame_id < total_frames:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_id)
            ret, frame = cap.read()
            if not ret:
                break
            timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
            yield timestamp, frame
            frame_id += frame_interval

        cap.release()

    return total_samples, generator()
