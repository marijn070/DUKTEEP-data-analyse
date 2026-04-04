from pathlib import Path

DUKTEEP_LINK = "https://www.youtube.com/@dukteep"
VIDEO_DIR = Path("videos")
FACE_PATHS_WITH_NAMES = {
    "marijn": "known_faces/marijn.png",
    "koen": "known_faces/koen.png",
    "angela": "known_faces/angela.jpg",
    "mees": "known_faces/mees.png",
}
DB_URI = "postgresql://postgres:postgres@localhost:5555/dukteep"
FRAME_INTERVAL = 1.0
MODEL_NAME = "Facenet"
DATABASE_TYPE = "pgvector"
SAMPLE_INTERVAL = 1.0
